package main

import (
    "context"
    "github.com/gorilla/handlers"
    "github.com/gorilla/mux"
    "log"
    "net/http"
    "time"
    "ymal-api-go/database"
    "ymal-api-go/routes"
)

type App struct {
    Router *mux.Router
}

type RequestHandlerFunction func(w http.ResponseWriter, r *http.Request)

func (app *App) handleRequest(handler RequestHandlerFunction) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        handler(w, r)
    }
}

func main() {
    headersOk := handlers.AllowedHeaders([]string{"X-Requested-With"})
    originsOk := handlers.AllowedOrigins([]string{"*"})
    methodsOk := handlers.AllowedMethods([]string{"GET", "HEAD", "POST", "PUT", "OPTIONS"})

    _, cancel := context.WithTimeout(context.Background(), 10 * time.Second)
    defer cancel()

    err := database.InitMongo()
    if err != nil {
        log.Fatal("Error init mongo")
    }

    app := App{Router: mux.NewRouter()}

    // requests
    app.Router.HandleFunc("/api/requests/getPastRequests", app.handleRequest(routes.GetPastRequests)).Methods("GET")
    app.Router.HandleFunc("/api/requests/getFutureRequests", app.handleRequest(routes.GetFutureRequests)).Methods("GET")
    app.Router.HandleFunc("/api/requests/createRequest", app.handleRequest(routes.CreateRequest)).Methods("POST")


    log.Fatal(http.ListenAndServe(":8000", handlers.CORS(originsOk, headersOk, methodsOk)(app.Router)))
}
