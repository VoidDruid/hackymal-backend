package routes

import (
    "encoding/json"
    "log"
    "net/http"
    "ymal-api-go/crud"
    "ymal-api-go/models"
)

func GetRequest(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")

    req := models.Request{
        Type: models.RequestTypeAI92K5,
        Date: "12.05.2021",
        Amount: 2000,
        Status: models.RequestStatusAccepted}

    _ = json.NewEncoder(w).Encode(req)
}

func CreateRequest(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")

    decoder := json.NewDecoder(r.Body)
    var requestPost models.RequestPost
    err := decoder.Decode(&requestPost)
    if err != nil {
        log.Println(err)
        w.WriteHeader(400)
        _ = json.NewEncoder(w).Encode(models.ErrorResult{Description: "invalid parameters"})
        return
    }

    req, err := crud.CreateRequestInDB(&requestPost)
    if err != nil {
        log.Println(err)
        w.WriteHeader(400)
        _ = json.NewEncoder(w).Encode(models.ErrorResult{Description: err.Error()})
        return
    }

    _ = json.NewEncoder(w).Encode(req)
}

func GetFutureRequests(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")

    city := r.URL.Query().Get("city")
    requests, err := crud.GetFutureRequestsFromDB(&city)
    if err != nil {
        log.Println(err)
        w.WriteHeader(400)
        _ = json.NewEncoder(w).Encode(models.ErrorResult{Description: err.Error()})
        return
    }

    if len(requests) != 0 {
        _ = json.NewEncoder(w).Encode(requests)
    } else {
        _ = json.NewEncoder(w).Encode([]models.Request{})
    }
}

func GetPastRequests(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")

    city := r.URL.Query().Get("city")
    requests, err := crud.GetPastRequestsFromDB(&city)
    if err != nil {
        log.Println(err)
        w.WriteHeader(400)
        _ = json.NewEncoder(w).Encode(models.ErrorResult{Description: err.Error()})
        return
    }

    if len(requests) != 0 {
        _ = json.NewEncoder(w).Encode(requests)
    } else {
        _ = json.NewEncoder(w).Encode([]models.Request{})
    }
}
