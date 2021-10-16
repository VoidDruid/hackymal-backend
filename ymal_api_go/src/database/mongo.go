package database

import (
    "context"
    "go.mongodb.org/mongo-driver/mongo"
    "go.mongodb.org/mongo-driver/mongo/options"
    "log"
    "os"
)
var ctx = context.TODO() // actually TODO

var db *mongo.Client = nil

func InitMongo() (err error) {
    MongoURI := os.Getenv("MONGO_URI")
    db, err = mongo.Connect(ctx, options.Client().ApplyURI(MongoURI))
    return
}

func GetMongo() *mongo.Client {
    if db == nil {
        err := InitMongo()
        if err != nil {
            log.Fatalln("Failed init mongo")
        }
    }
    return db
}