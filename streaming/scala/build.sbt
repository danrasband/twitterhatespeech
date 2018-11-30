name := "Final Project"

version := "1.0"

scalaVersion := "2.11.8"

libraryDependencies += "org.apache.spark" %% "spark-core" % "2.1.1"

libraryDependencies += "org.apache.spark" % "spark-streaming_2.11" % "2.1.1"

libraryDependencies += "org.apache.bahir" %% "spark-streaming-twitter" % "2.1.1"

// https://mvnrepository.com/artifact/com.google.code.gson/gson
// slibraryDependencies += "com.google.code.gson" % "gson" % "2.1.1"

resolvers += "Akka Repository" at "http://repo.akka.io/releases/"
