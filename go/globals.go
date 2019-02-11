package main

import (
	"github.com/cheggaaa/pb"
	"time"
)

////////////////////// ---------- globals -------------- //////////////////////

// these are all global variables, which is why they are Capitalized

var BeginTime = time.Now()
var GlobalOutputs Output
var RunName string
var Disallow_retest int

// var Query Query_t
var Output_dir = "go/tmp/cycle_state/"

var TbTestMonthCutoff uint
var TheSeed int64
var NumberOfPeople uint
var NumberOfPeopleStarting uint
var NumberOfIterations uint
var NumberOfPeopleEnteringPerYear uint
var NumberOfPeopleEntering uint
var NumberOfCycles uint
var SimName string
var IterationNum uint
var IsClosedCohort uint
var IterationSeed int
var NumberOfPeopleStartingByYear map[int]uint
var NumberOfPeopleEnteringByYear map[int]uint
var PsaNumberOfRuns int
var PsaRunNum int
var DsaRunNum int
var IsLow bool
var TestedThroughActiveCaseFinding int

// var AdjustedNumberOfPeopleEnteringByYear map[int]uint
var AdjustedNumberOfPeopleEnteringPerCycleByYear map[int]uint

var INF_TST_ID uint
var INF_QFT_ID uint
var INF_TSPOT_ID uint
var INF_TST_QFT_ID uint
var INF_TST_TSPOT_ID uint
var UNI_TST_ID uint
var UNI_QFT_ID uint
var UNI_TSPOT_ID uint
var UNI_TST_QFT_ID uint
var UNI_TST_TSPOT_ID uint

var LBTI_9M_INH uint
var LTBI_6M_INH uint
var LTBI_RIF uint
var LTBI_RTP uint
var FP_LBTI_9M_INH uint
var FP_LTBI_6M_INH uint
var FP_LTBI_RIF uint
var FP_LTBI_RTP uint

// var Treatment_choice_neg_id uint
// var Treatment_choice_pos_id uint

var TotalIpumsNew int
var TotalIpumsCurrent int

var InputsPath string
var IsProfile string
var RunType string
var RunAdjustment float64

var RandomLetters string

var Inputs Input
var Outputs Output
var Query Query_t
var Bar *pb.ProgressBar

var RandomController RandomController_t

var VariableCount uint
var WithinVariableCount uint

var InterventionId uint

var ReducedChains []Chain

var DATABASE_PATH string

var BIRTHPLACE_CHAIN_ID uint
var RACE_CHAIN_ID uint
var US_BIRTHPLACE_ID uint
var UNINF_TESTING_TST_ID uint

var FAST_LATENT_ID uint
var SLOW_LATENT_ID uint
var UNINF_ID uint

var ACTIVE_UNTREATED_ID uint
var ACTIVE_TREATED_M1_ID uint
var ACTIVE_TREATED_M2_ID uint
var ACTIVE_TREATED_M3_ID uint
var ACTIVE_TREATED_M4_ID uint
var ACTIVE_TREATED_M5_ID uint
var ACTIVE_TREATED_M6_ID uint
var DEFAULT_ID uint

var AGE_CHAIN_ID uint
var LEN_TIME_CHAIN_ID uint
var TB_CHAIN_ID uint

var HIV_CHAIN_ID uint
var DIABETES_CHAIN_ID uint
var HOMESLESSNESS_CHAIN_ID uint
var ESRD_CHAIN_ID uint
var TNF_CHAIN_ID uint
var SMOKER_CHAIN_ID uint
var TRANSPLANTS_CHAIN_ID uint
var HIVRISKGROUPS_CHAIN_ID uint
var ALCOHOL_CHAIN_ID uint
var SEX_CHAIN_ID uint
var MRF_CHAIN_ID uint
var DEATH_CHAIN_ID uint

var INFECTEDHIVNOART_STATE_ID uint
var INFECTEDHIVART_STATE_ID uint
var DIABETES_STATE_ID uint
var HOMELESS_STATE_ID uint
var ESRD_STATE_ID uint
var TNFALPHA_STATE_ID uint
var SMOKER_STATE_ID uint
var TRANSPLANTPATIENT_STATE_ID uint
var IDU_STATE_ID uint
var ALCOHOL_STATE_ID uint

func initializeConstants() {

	//testing
	INF_TST_ID = Query.getStateByName("Infected Testing TST").Id
	INF_QFT_ID = Query.getStateByName("Infected Testing QFT").Id
	INF_TSPOT_ID = Query.getStateByName("Infected Testing TSPOT").Id
	INF_TST_QFT_ID = Query.getStateByName("Infected Testing TST+QFT").Id
	INF_TST_TSPOT_ID = Query.getStateByName("Infected Testing TST+TSPOT").Id
	UNI_TST_ID = Query.getStateByName("Uninfected Testing TST").Id
	UNI_QFT_ID = Query.getStateByName("Uninfected Testing QFT").Id
	UNI_TSPOT_ID = Query.getStateByName("Uninfected Testing TSPOT").Id
	UNI_TST_QFT_ID = Query.getStateByName("Uninfected Testing TST+QFT").Id
	UNI_TST_TSPOT_ID = Query.getStateByName("Uninfected Testing TST+TSPOT").Id

	// treatment
	LBTI_9M_INH = Query.getStateByName("LBTI 9m INH - Month 1").Id
	LTBI_6M_INH = Query.getStateByName("LTBI 6m INH - Month 1").Id
	LTBI_RIF = Query.getStateByName("LTBI RIF - Month 1").Id
	LTBI_RTP = Query.getStateByName("LTBI RTP - Month 1").Id
	FP_LBTI_9M_INH = Query.getStateByName("FP LBTI 9m INH - Month 1").Id
	FP_LTBI_6M_INH = Query.getStateByName("FP LTBI 6m INH - Month 1").Id
	FP_LTBI_RIF = Query.getStateByName("FP LTBI RIF - Month 1").Id
	FP_LTBI_RTP = Query.getStateByName("FP LTBI RTP - Month 1").Id

	// chains
	BIRTHPLACE_CHAIN_ID = Query.getChainByName("Birthplace").Id
	RACE_CHAIN_ID = Query.getChainByName("Race").Id
	AGE_CHAIN_ID = Query.getChainByName("Age grouping").Id
	LEN_TIME_CHAIN_ID = Query.getChainByName("Length of time in US").Id
	TB_CHAIN_ID = Query.getChainByName("TB disease and treatment").Id
	HIV_CHAIN_ID = Query.getChainByName("HIV").Id
	DIABETES_CHAIN_ID = Query.getChainByName("Diabetes").Id
	HOMESLESSNESS_CHAIN_ID = Query.getChainByName("Homeless").Id
	ESRD_CHAIN_ID = Query.getChainByName("ESRD").Id
	TNF_CHAIN_ID = Query.getChainByName("TNF-alpha").Id
	SMOKER_CHAIN_ID = Query.getChainByName("Smoking").Id
	TRANSPLANTS_CHAIN_ID = Query.getChainByName("Transplants").Id
	HIVRISKGROUPS_CHAIN_ID = Query.getChainByName("HIV risk groups").Id
	ALCOHOL_CHAIN_ID = Query.getChainByName("Alcohol").Id
	US_BIRTHPLACE_ID = Query.getStateByName("United States").Id
	SEX_CHAIN_ID = Query.getChainByName("Sex").Id
	MRF_CHAIN_ID = Query.getChainByName("Medical risk factor").Id
	DEATH_CHAIN_ID = Query.getChainByName("Natural death").Id

	//states
	UNINF_TESTING_TST_ID = Query.getStateByName("Uninfected Testing TST").Id
	FAST_LATENT_ID = Query.getStateByName("Fast latent").Id
	SLOW_LATENT_ID = Query.getStateByName("Slow latent").Id
	UNINF_ID = Query.getStateByName("Uninfected TB").Id
	ACTIVE_UNTREATED_ID = Query.getStateByName("Active - untreated").Id
	ACTIVE_TREATED_M1_ID = Query.getStateByName("Active Treated Month 1").Id
	ACTIVE_TREATED_M2_ID = Query.getStateByName("Active Treated Month 2").Id
	ACTIVE_TREATED_M3_ID = Query.getStateByName("Active Treated Month 3").Id
	ACTIVE_TREATED_M4_ID = Query.getStateByName("Active Treated Month 4").Id
	ACTIVE_TREATED_M5_ID = Query.getStateByName("Active Treated Month 5").Id
	ACTIVE_TREATED_M6_ID = Query.getStateByName("Active Treated Month 6").Id
	DEFAULT_ID = Query.getStateByName("Default").Id

	INFECTEDHIVNOART_STATE_ID = Query.getStateByName("Infected HIV, no ART").Id
	INFECTEDHIVART_STATE_ID = Query.getStateByName("Infected HIV, ART").Id
	DIABETES_STATE_ID = Query.getStateByName("Diabetes").Id
	HOMELESS_STATE_ID = Query.getStateByName("Homeless").Id
	ESRD_STATE_ID = Query.getStateByName("ESRD").Id
	TNFALPHA_STATE_ID = Query.getStateByName("TNF-alpha").Id
	SMOKER_STATE_ID = Query.getStateByName("Smoker").Id
	TRANSPLANTPATIENT_STATE_ID = Query.getStateByName("Transplant patient").Id
	IDU_STATE_ID = Query.getStateByName("IDU").Id
	ALCOHOL_STATE_ID = Query.getStateByName("Alcohol").Id

}

////////////////////// ---------- types -------------- //////////////////////
