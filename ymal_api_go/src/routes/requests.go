package routes

import (
    "encoding/json"
    "log"
    "net/http"
    "strconv"
    "strings"
    "time"
    "ymal-api-go/crud"
    "ymal-api-go/models"
)

func buildStats(requests *[]models.Request) models.RequestStatCombined {
    if requests == nil {
        return models.RequestStatCombined{}
    }
    currentYear := strconv.FormatUint(uint64(time.Now().Year()), 10)
    previousYear := strconv.FormatUint(uint64(time.Now().Year() - 1), 10)
    log.Println(currentYear, previousYear)

    var combinedStat models.RequestStatCombined
    var currentYearStat models.RequestStat
    var previousYearStat models.RequestStat

    currentYearStat.Label = "Данные за " + currentYear + " год"
    previousYearStat.Label = "Данные за " + previousYear + " год"

    prevDTATU := models.RequestStatItem {Type: models.RequestTypeDTATU,Volume: 0}
    prevDTZGOST := models.RequestStatItem {Type: models.RequestTypeDTZGOST,Volume: 0}
    prevDTAGOST := models.RequestStatItem {Type: models.RequestTypeDTAGOST,Volume: 0}
    prevDTLGOST := models.RequestStatItem {Type: models.RequestTypeDTLGOST,Volume: 0}
    prevAI92K5 := models.RequestStatItem {Type: models.RequestTypeAI92K5,Volume: 0}

    curDTATU := models.RequestStatItem {Type: models.RequestTypeDTATU,Volume: 0}
    curDTZGOST := models.RequestStatItem {Type: models.RequestTypeDTZGOST,Volume: 0}
    curDTAGOST := models.RequestStatItem {Type: models.RequestTypeDTAGOST,Volume: 0}
    curDTLGOST := models.RequestStatItem {Type: models.RequestTypeDTLGOST,Volume: 0}
    curAI92K5 := models.RequestStatItem {Type: models.RequestTypeAI92K5,Volume: 0}

    currentYearStat.Items = []models.RequestStatItem{}
    previousYearStat.Items = []models.RequestStatItem{}

    for _, req := range *requests {
        if strings.Contains(req.Date, currentYear) {
            // current year
            if req.Type == models.RequestTypeDTATU {
                curDTATU.Volume+=req.Amount
            } else if req.Type == models.RequestTypeDTZGOST {
                curDTZGOST.Volume += req.Amount
            } else if req.Type == models.RequestTypeDTAGOST {
                curDTAGOST.Volume += req.Amount
            } else if req.Type == models.RequestTypeDTLGOST {
                curDTLGOST.Volume += req.Amount
            } else if req.Type == models.RequestTypeAI92K5 {
                curAI92K5.Volume += req.Amount
            }
        } else if strings.Contains(req.Date, previousYear) {
            if req.Type == models.RequestTypeDTATU {
                prevDTATU.Volume+=req.Amount
            } else if req.Type == models.RequestTypeDTZGOST {
                prevDTZGOST.Volume += req.Amount
            } else if req.Type == models.RequestTypeDTAGOST {
                prevDTAGOST.Volume += req.Amount
            } else if req.Type == models.RequestTypeDTLGOST {
                prevDTLGOST.Volume += req.Amount
            } else if req.Type == models.RequestTypeAI92K5 {
                prevAI92K5.Volume += req.Amount
            }
        }
    }

    currentYearStat.Items = append(currentYearStat.Items, curDTATU)
    currentYearStat.Items = append(currentYearStat.Items, curDTZGOST)
    currentYearStat.Items = append(currentYearStat.Items, curDTAGOST)
    currentYearStat.Items = append(currentYearStat.Items, curDTLGOST)
    currentYearStat.Items = append(currentYearStat.Items, curAI92K5)

    previousYearStat.Items = append(previousYearStat.Items, prevDTATU)
    previousYearStat.Items = append(previousYearStat.Items, prevDTZGOST)
    previousYearStat.Items = append(previousYearStat.Items, prevDTAGOST)
    previousYearStat.Items = append(previousYearStat.Items, prevDTLGOST)
    previousYearStat.Items = append(previousYearStat.Items, prevAI92K5)

    combinedStat.CurrentYear = currentYearStat
    combinedStat.PreviousYear = previousYearStat
    return combinedStat
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

    if r.URL.Query().Has("city") == false {
        w.WriteHeader(400)
        _ = json.NewEncoder(w).Encode(models.ErrorResult{Description:"empty city query parameter"})
        return
    }

    city := r.URL.Query().Get("city")
    limit, err := strconv.ParseInt(r.URL.Query().Get("limit"), 10, 32)
    if err != nil {
        limit = 15
    }

    requests, err := crud.GetFutureRequestsFromDB(&city)
    if err != nil {
        log.Println(err)
        w.WriteHeader(400)
        _ = json.NewEncoder(w).Encode(models.ErrorResult{Description: err.Error()})
        return
    }

    if len(requests) != 0 {
        if limit > int64(len(requests)) {
            limit = int64(len(requests))
        }
        _ = json.NewEncoder(w).Encode(requests[:limit])
    } else {
        _ = json.NewEncoder(w).Encode([]models.Request{})
    }
}

func GetPastRequests(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")

    if r.URL.Query().Has("city") == false {
        w.WriteHeader(400)
        _ = json.NewEncoder(w).Encode(models.ErrorResult{Description:"empty city query parameter"})
        return
    }

    city := r.URL.Query().Get("city")
    limit, err := strconv.ParseInt(r.URL.Query().Get("limit"), 10, 32)
    if err != nil {
        limit = 15
    }

    requests, err := crud.GetPastRequestsFromDB(&city)
    if err != nil {
        log.Println(err)
        w.WriteHeader(400)
        _ = json.NewEncoder(w).Encode(models.ErrorResult{Description: err.Error()})
        return
    }

    if len(requests) != 0 {
        if limit > int64(len(requests)) {
            limit = int64(len(requests))
        }
        _ = json.NewEncoder(w).Encode(requests[:limit])
    } else {
        _ = json.NewEncoder(w).Encode([]models.Request{})
    }
}

func GetRequestStatistics(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")

    if r.URL.Query().Has("city") == false {
        w.WriteHeader(400)
        _ = json.NewEncoder(w).Encode(models.ErrorResult{Description:"empty city query parameter"})
        return
    }

    city := r.URL.Query().Get("city")
    requests, err := crud.GetAllRequestsFromDB(&city)
    if err != nil {
        log.Println(err)
        w.WriteHeader(400)
        _ = json.NewEncoder(w).Encode(models.ErrorResult{Description: err.Error()})
        return
    }
    combinedStat := buildStats(&requests)
    _ = json.NewEncoder(w).Encode(combinedStat)
}
