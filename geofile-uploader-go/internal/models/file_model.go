package models

type FileResponse struct {
	Status   int     `json:"status"`
	Message  string  `json:"message"`
	Filename *string `json:"filename"`
}

type GenericResponse struct {
	Status  int    `json:"status"`
	Message string `json:"message"`
}
