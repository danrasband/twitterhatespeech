/**
 * Sources of inspiration
 * https://github.com/retroryan/twitter_classifier/blob/master/scala/src/main/scala/com/databricks/apps/twitter_classifier/Collect.scala
 * https://databricks.gitbooks.io/databricks-spark-reference-applications/content/twitter_classifier/collect.html
 */

import org.apache.log4j.{Level, Logger}

import org.apache.spark.streaming.{Seconds, Minutes, StreamingContext}
import org.apache.spark.streaming.twitter._
import org.apache.spark.{SparkConf, SparkContext}
import org.apache.spark.util.IntParam

import java.io.File
import scala.io.Source

object TwitterSelectedTags {

  def main(args: Array[String]) {

    // this controls a lot of spark related logging
    // comment or change logging level as needed
    Logger.getLogger("org").setLevel(Level.OFF);
    Logger.getLogger("akka").setLevel(Level.OFF);

    // Process program arguments and set properties
    if (args.length != 9) {
      System.err.println("USER INPUT ERROR")
      System.exit(1)
    }

    val intervalMins = args(0).toInt
    val users = Source.fromFile(args(1)).getLines.toSet
    val vocab = Source.fromFile(args(2)).getLines.toSet
    val outputDir = new File(args(3).toString)

    System.setProperty("twitter4j.oauth.consumerKey", args(4))
    System.setProperty("twitter4j.oauth.consumerSecret", args(5))
    System.setProperty("twitter4j.oauth.accessToken", args(6))
    System.setProperty("twitter4j.oauth.accessTokenSecret", args(7))

    val partitionsEachInterval = args(8).toInt

    var numTweetsCollected1 = 0L
    var numTweetsCollected2 = 0L

    if (outputDir.exists()) {
      System.err.println("ERROR - %s already exists: delete or specify another directory".format(
        args(3)))
      System.exit(1)
    }

    outputDir.mkdirs()

    println("Initializing Streaming Spark Context...")
    val conf = new SparkConf().setAppName(this.getClass.getSimpleName)
    val sc = new SparkContext(conf)
    val ssc = new StreamingContext(sc, Minutes(intervalMins))

    val tweetStream = TwitterUtils.createStream(ssc, None)

    val users_bc = sc.broadcast(users)
    val vocab_bc = sc.broadcast(vocab)

    def checkVocab (status: String) : Long = {
      val words : Array[String] = status.split(" ")
      var count_words = 0L
      for( word <- words ){
        val clean_word : String = word.replaceAll("[^a-zA-Z0-9]","").toLowerCase();
        if (vocab_bc.value.contains(clean_word)){
          count_words += 1
        }
      }
      return count_words
    }

    tweetStream.foreachRDD((rdd, time) => {
      println("New batch incoming...")
      val count_ttl = rdd.count()
      println("Number of tweets in the batch: %s".format(count_ttl))
      if (count_ttl > 0) {
        val userRDD = rdd.filter(status => status.getLang == "en")
                         .filter(status => users_bc.value.contains(status.getUser.getScreenName))
                         .map(status => (status.getId,
                                         status.getUser.getScreenName,
                                         status.getText.split('\n').map(_.trim.filter(_ >= ' ')).mkString,
                                         status.isTruncated,
                                         status.isRetweet,
                                         status.getRetweetCount,
                                         status.getFavoriteCount,
                                         status.isPossiblySensitive,
                                         checkVocab(status.getText)))
                         .coalesce(partitionsEachInterval)
                         .cache()

        val vocabRDD = rdd.filter(status => status.getLang == "en")
                          .filter(status => checkVocab(status.getText) > 0)
                          .map(status => (status.getId,
                                         status.getUser.getScreenName,
                                         status.getText.split('\n').map(_.trim.filter(_ >= ' ')).mkString,
                                         status.isTruncated,
                                         status.isRetweet,
                                         status.getRetweetCount,
                                         status.getFavoriteCount,
                                         status.isPossiblySensitive,
                                         checkVocab(status.getText)))
                          .coalesce(partitionsEachInterval)
                          .cache()

        userRDD.saveAsTextFile(args(3) + "/user_tweets_" + time.milliseconds.toString)
        vocabRDD.saveAsTextFile(args(3) + "/vocab_tweets_" + time.milliseconds.toString)

        val count_users = userRDD.count()
        val count_vocab = vocabRDD.count()
        numTweetsCollected1 += count_users
        numTweetsCollected2 += count_vocab
        println("Number of user matching tweets: %s".format(count_users))
        println("Number of vocab matching tweets: %s".format(count_vocab))
        println("Total number of user tweets collected: %s".format(numTweetsCollected1))
        println("Total number of vocab tweets collected: %s".format(numTweetsCollected2))
      }
    })

    ssc.start()
    ssc.awaitTermination()
  }
}
