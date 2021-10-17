package crud

import (
    "context"
    "errors"
    "fmt"
    "go.mongodb.org/mongo-driver/bson"
    "go.mongodb.org/mongo-driver/bson/primitive"
    "go.mongodb.org/mongo-driver/mongo"
    "log"
    "math/rand"
    "time"
    "ymal-api-go/database"
    "ymal-api-go/models"
)

func FromRequestPostToRequest(reqPost *models.RequestPost) (req models.Request, err error) {
    if reqPost == nil || reqPost.Type == nil || reqPost.Amount == nil || reqPost.City == nil {
        return models.Request{}, errors.New("invalid parameters")
    }

    req.Amount = *reqPost.Amount
    req.Type = *reqPost.Type
    req.City = *reqPost.City
    req.Status = models.RequestStatusNew

    t := time.Now()
    req.Date = fmt.Sprintf("%02d.%02d.%d",
        t.Day(), t.Month(), t.Year())
    return
}

func FloodDB(city string) {
    db := database.GetMongo()
    requests := db.Database("ymal").Collection("requests")
    requests.Drop(context.TODO())

    rand.Seed(time.Now().Unix())
    types := make([]string, 0, 5)
    types = append(types, models.RequestTypeAI92K5)
    types = append(types, models.RequestTypeDTAGOST)
    types = append(types, models.RequestTypeDTATU)
    types = append(types, models.RequestTypeDTLGOST)
    types = append(types, models.RequestTypeDTZGOST)

    // 2020
    for i:= 0; i < 25; i++ {
        var req models.RequestPost
        req.Type = new(string)
        *req.Type = types[rand.Intn(len(types))]
        req.City = new(string)
        *req.City = city
        req.Amount = new(uint)
        *req.Amount = uint(rand.Intn(100000))
        req.Date = new(string)
        t := time.Now()
        date := fmt.Sprintf("%02d.%02d.%d",
            t.Day() - 10, t.Month(), t.Year()-1)
        *req.Date = date
        CreateRequestInDB(&req)
    }
    for i:= 0; i < 25; i++ {
        var req models.RequestPost
        req.Type = new(string)
        *req.Type = types[rand.Intn(len(types))]
        req.City = new(string)
        *req.City = city
        req.Amount = new(uint)
        *req.Amount = uint(rand.Intn(100000))
        req.Date = new(string)
        t := time.Now()
        date := fmt.Sprintf("%02d.%02d.%d",
            t.Day(), t.Month(), t.Year()-1)
        *req.Date = date
        CreateRequestInDB(&req)
    }

    for i:= 0; i < 25; i++ {
        var req models.RequestPost
        req.Type = new(string)
        *req.Type = types[rand.Intn(len(types))]
        req.City = new(string)
        *req.City = city
        req.Amount = new(uint)
        *req.Amount = uint(rand.Intn(100000))
        req.Date = new(string)
        t := time.Now()
        date := fmt.Sprintf("%02d.%02d.%d",
            t.Day()+5, t.Month(), t.Year()-1)
        *req.Date = date
        CreateRequestInDB(&req)
    }
    // 2021
    for i:= 0; i < 25; i++ {
        var req models.RequestPost
        req.Type = new(string)
        *req.Type = types[rand.Intn(len(types))]
        req.City = new(string)
        *req.City = city
        req.Amount = new(uint)
        *req.Amount = uint(rand.Intn(100000))
        req.Date = new(string)
        t := time.Now()
        date := fmt.Sprintf("%02d.%02d.%d",
            t.Day() - 10, t.Month(), t.Year())
        *req.Date = date
        CreateRequestInDB(&req)
    }
    for i:= 0; i < 25; i++ {
        var req models.RequestPost
        req.Type = new(string)
        *req.Type = types[rand.Intn(len(types))]
        req.City = new(string)
        *req.City = city
        req.Amount = new(uint)
        *req.Amount = uint(rand.Intn(100000))
        req.Date = new(string)
        t := time.Now()
        date := fmt.Sprintf("%02d.%02d.%d",
            t.Day(), t.Month(), t.Year())
        *req.Date = date
        CreateRequestInDB(&req)
    }

    for i:= 0; i < 25; i++ {
        var req models.RequestPost
        req.Type = new(string)
        *req.Type = types[rand.Intn(len(types))]
        req.City = new(string)
        *req.City = city
        req.Amount = new(uint)
        *req.Amount = uint(rand.Intn(100000))
        req.Date = new(string)
        t := time.Now()
        date := fmt.Sprintf("%02d.%02d.%d",
            t.Day()+5, t.Month(), t.Year())
        *req.Date = date
        CreateRequestInDB(&req)
    }
}


func CreateRequestInDB(reqPost *models.RequestPost) (req models.Request, err error) {
    if reqPost == nil || reqPost.Type == nil || reqPost.Amount == nil || reqPost.City == nil {
        return models.Request{}, errors.New("invalid parameters")
    }

    req.Amount = *reqPost.Amount
    req.Type = *reqPost.Type
    req.City = *reqPost.City
    req.Status = models.RequestStatusNew

    if reqPost.Date != nil {
        req.Date = *reqPost.Date
    } else {
        t := time.Now()
        req.Date = fmt.Sprintf("%02d.%02d.%d",
        t.Day(), t.Month(), t.Year())
    }

    db := database.GetMongo()
    requests := db.Database("ymal").Collection("requests")

    var requestInDb models.Request
    err = requests.FindOne(context.TODO(), req).Decode(&requestInDb)
    if err == mongo.ErrNoDocuments {
        // not found
        _, err = requests.InsertOne(context.TODO(), req)
        return
    } else if err != nil {
        log.Println(err)
        return
    } else {
        req = requestInDb
        log.Println("Already exist")
        return
    }
}


func GetFutureRequestsFromDB(city *string) (reqs []models.Request, err error) {
    if city == nil {
        return []models.Request{}, errors.New("invalid city")
    }

    ctx := context.TODO()
    db := database.GetMongo()
    requests := db.Database("ymal").Collection("requests")
    cityFilter := "^" + *city + "$"
    filter := bson.D{{"city", primitive.Regex{Pattern: cityFilter, Options: ""}}}
    cur, err := requests.Find(ctx, filter)
    if err != nil {
        log.Println(err)
        return
    }
    defer func(cur *mongo.Cursor, ctx context.Context) {
        err := cur.Close(ctx)
        if err != nil {

        }
    }(cur, ctx)


    for cur.Next(ctx) {
        var req models.Request
        err := cur.Decode(&req)
        if err != nil {
            log.Println(err)
            continue
        }
        t, err := time.Parse("02.01.2006", req.Date)
        if err != nil {
            continue
        }

        now := time.Now()
        newT := now.Add(time.Hour * 5)
        currentDate := fmt.Sprintf("%02d.%02d.%d",
            newT.Day(), newT.Month(), newT.Year())
        if currentDate == req.Date {
            continue
        }

        if t.After(newT) {
            reqs = append(reqs, req)
        }
    }
    return
}

func GetPastRequestsFromDB(city *string) (reqs []models.Request, err error) {
    if city == nil {
        return []models.Request{}, errors.New("invalid city")
    }

    ctx := context.TODO()
    db := database.GetMongo()
    requests := db.Database("ymal").Collection("requests")
    cityFilter := "^" + *city + "$"
    filter := bson.D{{"city", primitive.Regex{Pattern: cityFilter, Options: ""}}}
    cur, err := requests.Find(ctx, filter)
    if err != nil {
        log.Println(err)
        return
    }
    defer func(cur *mongo.Cursor, ctx context.Context) {
        err := cur.Close(ctx)
        if err != nil {

        }
    }(cur, ctx)


    for cur.Next(ctx) {
        var req models.Request
        err := cur.Decode(&req)
        if err != nil {
            log.Println(err)
            continue
        }
        t, err := time.Parse("02.01.2006", req.Date)
        if err != nil {
            continue
        }

        now := time.Now()
        newT := now.Add(time.Hour * 5)
        currentDate := fmt.Sprintf("%02d.%02d.%d",
            newT.Day(), newT.Month(), newT.Year())

        if t.Before(newT) || currentDate == req.Date {
            reqs = append(reqs, req)
        }
    }
    return
}

func GetAllRequestsFromDB(city *string) (reqs []models.Request, err error) {
    if city == nil {
        return []models.Request{}, errors.New("invalid city")
    }

    ctx := context.TODO()
    db := database.GetMongo()
    requests := db.Database("ymal").Collection("requests")
    cityFilter := "^" + *city + "$"
    filter := bson.D{{"city", primitive.Regex{Pattern: cityFilter, Options: ""}}}
    cur, err := requests.Find(ctx, filter)
    if err != nil {
        log.Println(err)
        return
    }
    defer func(cur *mongo.Cursor, ctx context.Context) {
        err := cur.Close(ctx)
        if err != nil {

        }
    }(cur, ctx)


    for cur.Next(ctx) {
        var req models.Request
        err := cur.Decode(&req)
        if err != nil {
            log.Println(err)
            continue
        }
        reqs = append(reqs, req)
    }
    return
}
