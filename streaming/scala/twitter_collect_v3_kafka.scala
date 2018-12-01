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

import org.apache.kafka.clients.producer._

import java.io.File
import java.util.Properties

import scala.io.Source

object TwitterSelectedTags {
  type TweetData = Tuple9[Long, String, String, Boolean, Boolean, Int, Int, Boolean, Long]

  def main(args: Array[String]) {

    // this controls a lot of spark related logging
    // comment or change logging level as needed
    // Set logging level if log4j not configured (override by adding log4j.properties to classpath)
    if (!Logger.getRootLogger.getAllAppenders.hasMoreElements) {
      Logger.getRootLogger.setLevel(Level.WARN)
    }

    // Process program arguments and set properties
    if (args.length != 7) {
      System.err.println("USER INPUT ERROR")
      System.err.println(args.length.toString())
      System.exit(1)
    }

    val intervalSeconds = args(0).toInt
    val users = Source.fromFile(args(1)).getLines.toSet
    val vocab = Source.fromFile(args(2)).getLines.toSet

    System.setProperty("twitter4j.oauth.consumerKey", args(3))
    System.setProperty("twitter4j.oauth.consumerSecret", args(4))
    System.setProperty("twitter4j.oauth.accessToken", args(5))
    System.setProperty("twitter4j.oauth.accessTokenSecret", args(6))

    var numTweetsCollected1 = 0L
    var numTweetsCollected2 = 0L

    println("Initializing Streaming Spark Context...")
    val conf = new SparkConf().setAppName(this.getClass.getSimpleName)
    val sc = new SparkContext(conf)
    val ssc = new StreamingContext(sc, Seconds(intervalSeconds))

    val tweetStream = TwitterUtils.createStream(ssc, None)

    val users_bc = sc.broadcast(users)
    val vocab_bc = sc.broadcast(vocab)

    def checkUser (user: String) : Long = {
      var user_check = 0L
      if (users_bc.value.contains(user)){
        user_check = 1
      }
      return user_check
    }

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

    val kafkaProps = new Properties()
    kafkaProps.put("bootstrap.servers", "kafka.rasbonics.com:29092")
    kafkaProps.put("acks", "1")
    kafkaProps.put("key.serializer", "org.apache.kafka.common.serialization.StringSerializer")
    kafkaProps.put("value.serializer", "org.apache.kafka.common.serialization.StringSerializer")

    def sendToKafka (topic: String, tweetData: TweetData) {
      val kafkaProducer = new KafkaProducer[String, String](kafkaProps)
      val record = new ProducerRecord[String, String](topic, tweetData.toString())
      kafkaProducer.send(record)
      kafkaProducer.close()
    }

    tweetStream.foreachRDD((rdd, time) => {
      println("New batch incoming...")
      val count_ttl = rdd.count()
      println("Number of tweets in the batch: %s".format(count_ttl))
      if (count_ttl > 0) {
        val userRDD = rdd.filter(status => status.getLang == "en")
                         .filter(status => checkUser(status.getUser.getScreenName) > 0)
                         .map(status => new TweetData(status.getId,
                                         status.getUser.getScreenName,
                                         status.getText.split('\n').map(_.trim.filter(_ >= ' ')).mkString,
                                         status.isTruncated,
                                         status.isRetweet,
                                         status.getRetweetCount,
                                         status.getFavoriteCount,
                                         status.isPossiblySensitive,
                                         checkVocab(status.getText)))

        val vocabRDD = rdd.filter(status => status.getLang == "en")
                          .filter(status => checkVocab(status.getText) > 0)
                          .map(status => new TweetData(status.getId,
                                         status.getUser.getScreenName,
                                         status.getText.split('\n').map(_.trim.filter(_ >= ' ')).mkString,
                                         status.isTruncated,
                                         status.isRetweet,
                                         status.getRetweetCount,
                                         status.getFavoriteCount,
                                         status.isPossiblySensitive,
                                         checkVocab(status.getText)))

        userRDD.foreach(tweet => sendToKafka("tweets-users", tweet))
        vocabRDD.foreach(tweet => sendToKafka("tweets-vocab", tweet))

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
