package models

type ErrorResult struct {
    Description string
}

const(
    RequestStatusNew string = "Новая"
    RequestStatusAccepted = "Согласована"
)

const(
    RequestTypeDTATU string = "ДТ \"А\" ТУ"
    RequestTypeDTZGOST = "ДТ \"З\" ГОСТ"
    RequestTypeDTAGOST = "ДТ \"А\" ГОСТ"
    RequestTypeDTLGOST = "ДТ \"Л\" ГОСТ"
    RequestTypeAI92K5 = "АИ-92-К5"
)

type Request struct {
    Date string `json:"date"` // dd.mm.yyyy
    Type string `json:"type"`
    Amount uint `json:"amount"`
    Status string `json:"status"`
    City string `json:"city"`
}

type RequestPost struct {
    Date *string `json:"date"` // dd.mm.yyyy
    Type *string `json:"type"`
    Amount *uint `json:"amount"`
    City *string `json:"city"`
}

type RequestStatItem struct {
    Volume uint `json:"volume"`
    Type string `json:"type"`
}

type RequestStat struct {
    Label string `json:"label"`
    Items []RequestStatItem `json:"items"`
}

type RequestStatCombined struct {
    CurrentYear RequestStat `json:"current_year"`
    PreviousYear RequestStat `json:"previous_year"`
}
