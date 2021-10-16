package routes

import (
    "encoding/json"
    "net/http"
)

type Kek struct {
    Ok bool
}

func GetKey(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")

    w.WriteHeader(500)
    _ = json.NewEncoder(w).Encode(Kek{Ok:false})
}
