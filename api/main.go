package api

import (
	"log"

	"github.com/gin-gonic/gin"
)

// NewAPI returns a new instance of the Gin API
func NewAPI() *gin.Engine {
	log.Printf("Ripley API cold start")
	r := gin.Default()
	r.GET("/ping", func(c *gin.Context) {
		c.JSON(200, gin.H{
			"message": "pong",
		})
	})

	return r
}

func foo() {

}
