package api

import (
	"encoding/json"
	"time"
)

type waterEntry struct {
	KibbleEaten bool   `json:"kibble_eaten"`
	Notes       string `json:"notes"`
	Water       int    `json:"water"`
}

// JSON cannot unmarshall a string like "2020-04-04" to Go type time.Time
// so we need a custom type with a custom UnmarshalJSON() method to handle it.
type justADate time.Time

func (d *justADate) UnmarshalJSON(bs []byte) error {
	var s string
	err := json.Unmarshal(bs, &s)
	if err != nil {
		return err
	}
	t, err := time.ParseInLocation("2006-01-02", s, time.UTC)
	if err != nil {
		return err
	}
	*d = justADate(t)
	return nil
}

// MarshalJSON writes a quoted string in the custom format
func (d *justADate) MarshalJSON() ([]byte, error) {
	return []byte(d.String()), nil
}

func (d *justADate) String() string {
	t := time.Time(*d)
	return t.Format("2006-01-02")
}

type newWaterRequest struct {
	Date        justADate `json:"date" binding:"required" time_format:"2006-01-02"`
	KibbleEaten bool      `json:"kibble_eaten"`
	Notes       string    `json:"notes"`
	Water       int       `json:"water" binding:"required"`
}

func (w *newWaterRequest) convertWater() int {
	return waterStartAmount - (w.Water - waterBowlWeight)
}

type fitbarkActivityRequest struct {
	Resolution   string `form:"resolution" binding:"required,oneof=hourly daily"`
	NumberOfDays int    `form:"numberOfDays" binding:"required"`
}

type fitbarkActivityRecordDaily struct {
	Date            string `json:"date"`
	ActivityValue   uint   `json:"activity_value"`
	ActivityAverage uint   `json:"activity_average"`
	MinActive       uint   `json:"min_active"`
	MinPlay         uint   `json:"min_play"`
	MinRest         uint   `json:"min_rest"`
	DailyTarget     uint   `json:"daily_target"`
	HasTrophy       uint   `json:"has_trophy"`
}

type fitbarkActivityRecordHourly struct {
	Date            string  `json:"date"`
	Time            string  `json:"time"`
	ActivityValue   uint    `json:"activity_value"`
	MinActive       uint    `json:"min_active"`
	MinPlay         uint    `json:"min_play"`
	MinRest         uint    `json:"min_rest"`
	ActivityGoal    uint    `json:"activity_goal"`
	DistanceInMiles float32 `json:"distance_in_miles"`
	KCalories       uint    `json:"kcalories"`
}

type changeLogRecord struct {
	MessageHash string `json:"messageHash"`
	Date        string `json:"date"`
	Message     string `json:"message"`
	Type        string `json:"type"`
}

type bloodworkRecord struct {
	Date               string  `json:"date"`
	AbsBasophils       uint    `json:"Abs Basophils"`
	AbsEosinophils     uint    `json:"Abs Eosinophils"`
	AbsLymphocytes     uint    `json:"Abs Lymphocytes"`
	AbsMonocytes       uint    `json:"Abs Monocytes"`
	AbsNeutrophils     uint    `json:"Abs Neutrophils"`
	Bands              uint    `json:"Bands"`
	BasophilsPercent   float32 `json:"Basophils %"`
	EosinophilsPercent float32 `json:"Eosinophils %"`
	LymphocytesPercent float32 `json:"Lymphocytes %"`
	MonocytesPercent   float32 `json:"Monocytes %"`
	NeutrophilsPercent float32 `json:"Neutrophils %"`
	HCT                float32 `json:"HCT"`
	HGB                float32 `json:"HGB"`
	MCH                float32 `json:"MCH"`
	MCHC               float32 `json:"MCHC"`
	MCV                float32 `json:"MCV"`
	PlaeletCount       uint    `json:"Plaelet Count"`
	RBC                float32 `json:"RBC"`
	WBC                float32 `json:"WBC"`
}

type bloodworkLabel struct {
	Name  string  `json:"name"`
	Lower float32 `json:"lower"`
	Upper float32 `json:"upper"`
}
