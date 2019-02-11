///////

// TODO: stratification system
// TODO: sync system
// TODO: Initialization phase - one cycle; then model phase
// TODO: I think eventually it makes sense to make it all 1-indexed
// instead of zero-indexed. will require strict getters and setters.

////////////////////// ---------- start -------------- //////////////////////

package main

import (
	"fmt"
	"github.com/agoussia/godes"
	// "github.com/cheggaaa/pb"
	"github.com/fatih/structs"
	_ "github.com/mattn/go-sqlite3"
	// "github.com/mgutz/ansi"
	// "github.com/davecheney/profile"
	"gopkg.in/yaml.v2"
	"hash/fnv"
	"io/ioutil"
	"log"
	"math"
	"math/rand"
	"os"
	"runtime"
	"strconv"
	"sync"
	"time"
)

func printMemoryUse(msg string) {
	// fmt.Println(" ================== ", msg, " ================ ")

	// var mem runtime.MemStats

	// runtime.ReadMemStats(&mem)

	// fmt.Println("mem.Alloc: ", mem.Alloc/1000000.0, "M")
	// fmt.Println("mem.TotalAlloc: ", mem.TotalAlloc/1000000.0, "M")
	// fmt.Println("mem.HeapAlloc: ", mem.HeapAlloc/1000000.0, "M")
	// fmt.Println("mem.HeapSys: ", mem.HeapSys/1000000.0, "M")
	// fmt.Println("mem.Frees: ", mem.Frees/1000000.0, "M")
	// fmt.Println("mem.HeapObjects: ", mem.HeapObjects)
	// fmt.Println("(mem.Alloc - these are the bytes that were allocated and still in use, mem.TotalAlloc - what we allocated throughout the lifetime, mem.HeapAlloc - what’s being used on the heap right now, mem.HeapSys - this includes what is being used by the heap and what has been reclaimed but not given back out)")

}

func beginAnalysis(size string, NumberOfCycles uint, NumberOfIterations uint, SimName string, IsClosedCohort uint, adjustmentFactor float64) {

	// cfg := profile.Config{
	// 	CPUProfile: true,
	// 	// MemProfile:     true,
	// 	ProfilePath:    ".",  // store profiles in current directory
	// 	NoShutdownHook: true, // do not hook SIGINT
	// }
	// p.Stop() must be called before the program exits to
	// ensure profiling information is written to disk.

	// p := profile.Start(&cfg)

	TheSeed = time.Now().UTC().UnixNano()

	fmt.Println("Using seed of ... ", TheSeed)
	rand.Seed(TheSeed)

	SimName = SimName

	// Hi from LIMCAT
	show_greeting()

	//printMemoryUse("Before simluation")

	// print name of sim
	fmt.Println("Running simulation: ", SimName)

	fmt.Println("With this many runs", NumberOfIterations)

	NumberOfPeopleStartingByYear = make(map[int]uint)
	NumberOfPeopleEnteringByYear = make(map[int]uint)

	NumberOfPeopleStartingByYear[2001] = 25534900.0 //26657082.0 // this estimate is from CA Dept of Fin. was previous (from IPUMS) 25534900.0
	NumberOfPeopleStartingByYear[2014] = 31206652.0

	NumberOfPeopleEnteringByYear[2001] = 1163173.0 //569885.0
	NumberOfPeopleEnteringByYear[2002] = 1100130.0 //526445.0
	NumberOfPeopleEnteringByYear[2003] = 1103093.0 //548132.0
	NumberOfPeopleEnteringByYear[2004] = 1127722.0 //591289.0
	NumberOfPeopleEnteringByYear[2005] = 1161383.0 //619247.0
	NumberOfPeopleEnteringByYear[2006] = 1259438.0 //632620.0
	NumberOfPeopleEnteringByYear[2007] = 1205765.0 //611119.0
	NumberOfPeopleEnteringByYear[2008] = 1183370.0 //577231.0
	NumberOfPeopleEnteringByYear[2009] = 1114440.0 //550541.0
	NumberOfPeopleEnteringByYear[2010] = 1141379.0 //583596.0
	NumberOfPeopleEnteringByYear[2011] = 1149439.0 //569812.0
	NumberOfPeopleEnteringByYear[2012] = 1163563.0 //559316.0
	NumberOfPeopleEnteringByYear[2013] = 1171139.0 //568943.0
	NumberOfPeopleEnteringByYear[2014] = 1188697.0 //564637.0

	// if size == "s" {
	// 	adjustmentFactor = 1000
	// } else if size == "m" {
	// 	adjustmentFactor = 100
	// } else if size == "l" {
	// 	adjustmentFactor = 10
	// }

	var start_year int

	if RunType == "calib" || RunType == "psa" || RunType == "dsa" {
		start_year = 2001
	} else {
		start_year = 2014
	}

	NumberOfPeopleStarting = uint(float64(NumberOfPeopleStartingByYear[start_year]) / adjustmentFactor)

	AdjustedNumberOfPeopleEnteringPerCycleByYear = make(map[int]uint)

	NumberOfPeopleEntering = 0
	for i := 0; i < (int(NumberOfCycles) + 1); i++ {
		var year int
		if RunType == "calib" || RunType == "psa" || RunType == "dsa" {
			year = 2001 + int(math.Floor(float64(i)/float64(12)))
			// if modeling past 2014, just assume 2014
			if year > 2014 {
				year = 2014
			}
		} else {
			// if starting at 2014 (not calib), just keep using 2014
			year = 2014
		}

		enteringThisCycleUnadj := NumberOfPeopleEnteringByYear[year] / 12
		enteringThisCycleAdj := uint(math.Floor(float64(enteringThisCycleUnadj) / adjustmentFactor))
		AdjustedNumberOfPeopleEnteringPerCycleByYear[year] = enteringThisCycleAdj
		if IsClosedCohort == 1 {
			AdjustedNumberOfPeopleEnteringPerCycleByYear[year] = 0
		}

		NumberOfPeopleEntering = NumberOfPeopleEntering + enteringThisCycleAdj

	}

	if IsClosedCohort == 1 {
		NumberOfPeopleEntering = 0
	}

	if Disallow_retest == 1 {
		fmt.Println("NO RE-TESTING")
	} else {
		fmt.Println("RE-TESTING ALLOWED")
	}

	NumberOfPeople = NumberOfPeopleEntering + NumberOfPeopleStarting

	RunAdjustment = adjustmentFactor

	fmt.Println("and ", NumberOfPeopleStarting, "initial individuals")
	fmt.Println("and ", NumberOfPeopleEntering, "individuals entering")
	fmt.Println("and ", NumberOfPeople, "total")

	setEnvironment()

	TestedThroughActiveCaseFinding = 0

	initializeInputs(NumberOfCycles)

	// get variables from database
	initializeVariables()

	if RunType == "psa" || RunType == "dsa" {
		copyOriginalVariablesPsa()
	}

	Query.setUp()
	// use the variables to calculate parts of the transition probabilties
	calculateVariables()

	//printMemoryUse("After query set-up")

	initializeConstants()

	if RunType == "psa" {
		for i := 0; i < PsaNumberOfRuns; i++ {

			modifyInputsForPsa()

			// re-run variable calculation to propograte changes in variables
			calculateVariables()
			PsaRunNum = i
			runInterventions(NumberOfIterations)

			makeOutputs()
			GlobalOutputs.OutputsByCycle = []OutputByCycle{}
			GlobalOutputs.OutputsByCycleStateFull = []OutputByCycleState{}

		}

	} else if RunType == "dsa" {

		// variables

		numberOfVariablesForDsa := 85
		for i := 0; i < numberOfVariablesForDsa; i++ {

			// low

			IsLow = true
			modifyVariablesForDsa(i)

			// re-run variable calculation to propograte changes in variables
			calculateVariables()
			DsaRunNum = i
			runInterventions(NumberOfIterations)

			makeOutputs()
			GlobalOutputs.OutputsByCycle = []OutputByCycle{}
			GlobalOutputs.OutputsByCycleStateFull = []OutputByCycleState{}

			// high

			IsLow = false
			modifyVariablesForDsa(i)

			// re-run variable calculation to propograte changes in variables
			calculateVariables()
			DsaRunNum = i
			runInterventions(NumberOfIterations)

			makeOutputs()
			GlobalOutputs.OutputsByCycle = []OutputByCycle{}
			GlobalOutputs.OutputsByCycleStateFull = []OutputByCycleState{}

		}

		// transition probablitities

	} else {
		runInterventions(NumberOfIterations)
		makeOutputs()
		//printMemoryUse("after simulation")
	}

	// p.Stop()

}

// this copies best estimates to "original_base" for the PSA
func copyOriginalVariablesPsa() {
	// ---- transition probabilities -----
	for i := 0; i < len(Inputs.TransitionProbabilities); i++ {
		Inputs.TransitionProbabilities[i].Original_base = Inputs.TransitionProbabilities[i].Tp_base
	}

	variableList := []*Variable{&AccessMonthlyProportionOfTrueNegativesThatAreTested, &AccessMonthlyProportionOfTruePositivesThatAreTested, &UsbTstSensitivity, &UsbTstSpecificity, &UsbQftSensitivity, &UsbQftSpecificity, &UsbTspotSensitivity, &UsbTspotSpecificity, &FbTstSensitivity, &FbTstSpecificity, &FbQftSensitivity, &FbQftSpecificity, &FbTspotSensitivity, &FbTspotSpecificity, &HivTstSensitivity, &HivTstSpecificity, &HivQftSensitivity, &HivQftSpecificity, &HivTspotSensitivity, &HivTspotSpecificity, &EsrdTstSensitivity, &EsrdTstSpecificity, &EsrdQftSensitivity, &EsrdQftSpecificity, &EsrdTspotSensitivity, &EsrdTspotSpecificity, &ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveTstLtbiTest, &ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveQftTspotTest, &NumberOfLtbiCasesCausedByOneActiveCase, &NumberOfSecondaryTbCasesCausedByOneActiveCase, &EfficacyOf9H, &EfficacyOf6H, &EfficacyOf4R, &EfficacyOf3Hp, &BaseRiskOfProgression, &ProportionOfLtbiTreated, &FastLatentProgression, &SlowLatentProgression, &TotalCostOfLtbiTreatment9H, &TotalCostOfLtbiTreatment6H, &TotalCostOfLtbiTreatment4R, &TotalCostOfLtbiTreatment3Hp, &ProportionOfStartedWhoCompleteTreatment9H, &ProportionOfStartedWhoCompleteTreatment6H, &ProportionOfStartedWhoCompleteTreatment4R, &ProportionOfStartedWhoCompleteTreatment3Hp, &CostOfTst, &CostOfQft, &CostOfTspot, &CostOfTstQft, &CostOfTstTspot, &CostOfActiveTbCase, &QalysGainedAvertingOneCaseOfActiveTb, &LtbiOverallAdjustmentStarting, &LtbiOverallFbAdjustmentStarting, &LtbiOverallUsbAdjustmentStarting, &LtbiAsianFbAdjustmentStarting, &LtbiAsianUsbAdjustmentStarting, &LtbiWhiteFbAdjustmentStarting, &LtbiWhiteUsbAdjustmentStarting, &LtbiHispanicFbAdjustmentStarting, &LtbiHispanicUsbAdjustmentStarting, &LtbiBlackFbAdjustmentStarting, &LtbiBlackUsbAdjustmentStarting, &LtbiOtherFbAdjustmentStarting, &LtbiOtherUsbAdjustmentStarting, &LtbiOverallAdjustment, &LtbiOverallFbAdjustment, &LtbiOverallUsbAdjustment, &LtbiAsianFbAdjustment, &LtbiAsianUsbAdjustment, &LtbiWhiteFbAdjustment, &LtbiWhiteUsbAdjustment, &LtbiHispanicFbAdjustment, &LtbiHispanicUsbAdjustment, &LtbiBlackFbAdjustment, &LtbiBlackUsbAdjustment, &LtbiOtherFbAdjustment, &LtbiOtherUsbAdjustment, &DiabetesPrevalenceAdjustment, &EsrdPrevalenceAdjustment, &SmokerPrevalenceAdjustment, &TnfAlphaPrevalenceAdjustment, &HivPrevalenceAdjustment, &TransplantsPrevalenceAdjustment}

	for i := 0; i < len(variableList); i++ {
		variableList[i].Original_base = variableList[i].Value
	}

}

func modifyInputsForPsa() {

	tgGen := godes.NewTriangularDistr(false)

	// ------------- Transition probabilities ------------------

	fmt.Println("----- modifying TPs --------")

	for i := 0; i < len(Inputs.TransitionProbabilities); i++ {

		req := !Inputs.TransitionProbabilities[i].Is_dynamic &&
			!Inputs.TransitionProbabilities[i].Is_stratified &&
			Inputs.States[Inputs.TransitionProbabilities[i].From_state_id].Name != "Uninitialized" &&
			Inputs.TransitionProbabilities[i].From_state_id != Inputs.TransitionProbabilities[i].To_state_id

		if req {

			low := Inputs.TransitionProbabilities[i].Low
			high := Inputs.TransitionProbabilities[i].High
			middle := Inputs.TransitionProbabilities[i].Original_base

			Inputs.TransitionProbabilities[i].Tp_base = tgGen.Get(low, middle, high)
			// from := Inputs.States[Inputs.TransitionProbabilities[i].From_state_id].Name
			// to := Inputs.States[Inputs.TransitionProbabilities[i].To_state_id].Name

			checkLowMiddleHigh(low, middle, high)
			// fmt.Println(from, " -> ", to)
			// fmt.Println("L M H: ", low, middle, high, " Chosen: ", Inputs.TransitionProbabilities[i].Tp_base)
		}

	}

	// ------------- Variables ------------------

	fmt.Println("----- modifying vars --------")

	fmt.Println("NumberOfLtbiCasesCausedByOneActiveCase before:", NumberOfLtbiCasesCausedByOneActiveCase)

	variableList := []*Variable{&AccessMonthlyProportionOfTrueNegativesThatAreTested, &AccessMonthlyProportionOfTruePositivesThatAreTested, &UsbTstSensitivity, &UsbTstSpecificity, &UsbQftSensitivity, &UsbQftSpecificity, &UsbTspotSensitivity, &UsbTspotSpecificity, &FbTstSensitivity, &FbTstSpecificity, &FbQftSensitivity, &FbQftSpecificity, &FbTspotSensitivity, &FbTspotSpecificity, &HivTstSensitivity, &HivTstSpecificity, &HivQftSensitivity, &HivQftSpecificity, &HivTspotSensitivity, &HivTspotSpecificity, &EsrdTstSensitivity, &EsrdTstSpecificity, &EsrdQftSensitivity, &EsrdQftSpecificity, &EsrdTspotSensitivity, &EsrdTspotSpecificity, &ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveTstLtbiTest, &ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveQftTspotTest, &NumberOfLtbiCasesCausedByOneActiveCase, &NumberOfSecondaryTbCasesCausedByOneActiveCase, &EfficacyOf9H, &EfficacyOf6H, &EfficacyOf4R, &EfficacyOf3Hp, &BaseRiskOfProgression, &ProportionOfLtbiTreated, &FastLatentProgression, &SlowLatentProgression, &TotalCostOfLtbiTreatment9H, &TotalCostOfLtbiTreatment6H, &TotalCostOfLtbiTreatment4R, &TotalCostOfLtbiTreatment3Hp, &ProportionOfStartedWhoCompleteTreatment9H, &ProportionOfStartedWhoCompleteTreatment6H, &ProportionOfStartedWhoCompleteTreatment4R, &ProportionOfStartedWhoCompleteTreatment3Hp, &CostOfTst, &CostOfQft, &CostOfTspot, &CostOfTstQft, &CostOfTstTspot, &CostOfActiveTbCase, &QalysGainedAvertingOneCaseOfActiveTb, &LtbiOverallAdjustmentStarting, &LtbiOverallFbAdjustmentStarting, &LtbiOverallUsbAdjustmentStarting, &LtbiAsianFbAdjustmentStarting, &LtbiAsianUsbAdjustmentStarting, &LtbiWhiteFbAdjustmentStarting, &LtbiWhiteUsbAdjustmentStarting, &LtbiHispanicFbAdjustmentStarting, &LtbiHispanicUsbAdjustmentStarting, &LtbiBlackFbAdjustmentStarting, &LtbiBlackUsbAdjustmentStarting, &LtbiOtherFbAdjustmentStarting, &LtbiOtherUsbAdjustmentStarting, &LtbiOverallAdjustment, &LtbiOverallFbAdjustment, &LtbiOverallUsbAdjustment, &LtbiAsianFbAdjustment, &LtbiAsianUsbAdjustment, &LtbiWhiteFbAdjustment, &LtbiWhiteUsbAdjustment, &LtbiHispanicFbAdjustment, &LtbiHispanicUsbAdjustment, &LtbiBlackFbAdjustment, &LtbiBlackUsbAdjustment, &LtbiOtherFbAdjustment, &LtbiOtherUsbAdjustment, &DiabetesPrevalenceAdjustment, &EsrdPrevalenceAdjustment, &SmokerPrevalenceAdjustment, &TnfAlphaPrevalenceAdjustment, &HivPrevalenceAdjustment, &TransplantsPrevalenceAdjustment}

	for i := 0; i < len(variableList); i++ {

		low := variableList[i].Low
		high := variableList[i].High
		middle := variableList[i].Original_base

		variableList[i].Value = tgGen.Get(low, middle, high)

		checkLowMiddleHigh(low, middle, high)
		fmt.Println(variableList[i].Name)
		fmt.Println("L M H: ", low, middle, high, " Chosen: ", variableList[i].Value)

	}

	fmt.Println("NumberOfLtbiCasesCausedByOneActiveCase after:", NumberOfLtbiCasesCausedByOneActiveCase)

	// transition probabilities

}

func modifyVariablesForDsa(varInt int) {

	variableList := []*Variable{&AccessMonthlyProportionOfTrueNegativesThatAreTested, &AccessMonthlyProportionOfTruePositivesThatAreTested, &UsbTstSensitivity, &UsbTstSpecificity, &UsbQftSensitivity, &UsbQftSpecificity, &UsbTspotSensitivity, &UsbTspotSpecificity, &FbTstSensitivity, &FbTstSpecificity, &FbQftSensitivity, &FbQftSpecificity, &FbTspotSensitivity, &FbTspotSpecificity, &HivTstSensitivity, &HivTstSpecificity, &HivQftSensitivity, &HivQftSpecificity, &HivTspotSensitivity, &HivTspotSpecificity, &EsrdTstSensitivity, &EsrdTstSpecificity, &EsrdQftSensitivity, &EsrdQftSpecificity, &EsrdTspotSensitivity, &EsrdTspotSpecificity, &ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveTstLtbiTest, &ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveQftTspotTest, &NumberOfLtbiCasesCausedByOneActiveCase, &NumberOfSecondaryTbCasesCausedByOneActiveCase, &EfficacyOf9H, &EfficacyOf6H, &EfficacyOf4R, &EfficacyOf3Hp, &BaseRiskOfProgression, &ProportionOfLtbiTreated, &FastLatentProgression, &SlowLatentProgression, &TotalCostOfLtbiTreatment9H, &TotalCostOfLtbiTreatment6H, &TotalCostOfLtbiTreatment4R, &TotalCostOfLtbiTreatment3Hp, &ProportionOfStartedWhoCompleteTreatment9H, &ProportionOfStartedWhoCompleteTreatment6H, &ProportionOfStartedWhoCompleteTreatment4R, &ProportionOfStartedWhoCompleteTreatment3Hp, &CostOfTst, &CostOfQft, &CostOfTspot, &CostOfTstQft, &CostOfTstTspot, &CostOfActiveTbCase, &QalysGainedAvertingOneCaseOfActiveTb, &LtbiOverallAdjustmentStarting, &LtbiOverallFbAdjustmentStarting, &LtbiOverallUsbAdjustmentStarting, &LtbiAsianFbAdjustmentStarting, &LtbiAsianUsbAdjustmentStarting, &LtbiWhiteFbAdjustmentStarting, &LtbiWhiteUsbAdjustmentStarting, &LtbiHispanicFbAdjustmentStarting, &LtbiHispanicUsbAdjustmentStarting, &LtbiBlackFbAdjustmentStarting, &LtbiBlackUsbAdjustmentStarting, &LtbiOtherFbAdjustmentStarting, &LtbiOtherUsbAdjustmentStarting, &LtbiOverallAdjustment, &LtbiOverallFbAdjustment, &LtbiOverallUsbAdjustment, &LtbiAsianFbAdjustment, &LtbiAsianUsbAdjustment, &LtbiWhiteFbAdjustment, &LtbiWhiteUsbAdjustment, &LtbiHispanicFbAdjustment, &LtbiHispanicUsbAdjustment, &LtbiBlackFbAdjustment, &LtbiBlackUsbAdjustment, &LtbiOtherFbAdjustment, &LtbiOtherUsbAdjustment, &DiabetesPrevalenceAdjustment, &EsrdPrevalenceAdjustment, &SmokerPrevalenceAdjustment, &TnfAlphaPrevalenceAdjustment, &HivPrevalenceAdjustment, &TransplantsPrevalenceAdjustment}

	// reset all variables to their original

	for i := 0; i < len(variableList); i++ {
		variableList[i].Value = variableList[i].Original_base
	}

	// set target var to high or low

	for i := 0; i < len(variableList); i++ {
		if i == varInt {
			if IsLow {
				variableList[i].Value = variableList[i].Low
			} else {
				variableList[i].Value = variableList[i].High
			}
		}

	}

	fmt.Println("Setting variable ", variableList[varInt].Name, " as ", variableList[varInt].Value)

	// tgGen := godes.NewTriangularDistr(false)

	// // ------------- Transition probabilities ------------------

	// fmt.Println("----- modifying TPs --------")

	// for i := 0; i < len(Inputs.TransitionProbabilities); i++ {

	// 	req := !Inputs.TransitionProbabilities[i].Is_dynamic &&
	// 		!Inputs.TransitionProbabilities[i].Is_stratified &&
	// 		Inputs.States[Inputs.TransitionProbabilities[i].From_state_id].Name != "Uninitialized" &&
	// 		Inputs.TransitionProbabilities[i].From_state_id != Inputs.TransitionProbabilities[i].To_state_id

	// 	if req {

	// 		low := Inputs.TransitionProbabilities[i].Low
	// 		high := Inputs.TransitionProbabilities[i].High
	// 		middle := Inputs.TransitionProbabilities[i].Original_base

	// 		Inputs.TransitionProbabilities[i].Tp_base = tgGen.Get(low, middle, high)
	// 		// from := Inputs.States[Inputs.TransitionProbabilities[i].From_state_id].Name
	// 		// to := Inputs.States[Inputs.TransitionProbabilities[i].To_state_id].Name

	// 		checkLowMiddleHigh(low, middle, high)
	// 		// fmt.Println(from, " -> ", to)
	// 		// fmt.Println("L M H: ", low, middle, high, " Chosen: ", Inputs.TransitionProbabilities[i].Tp_base)
	// 	}

	// }

	// // ------------- Variables ------------------

	// fmt.Println("----- modifying vars --------")

	// fmt.Println("UsbTstSpecificity before:", UsbTstSpecificity)

	// for i := 0; i < len(variableList); i++ {

	// 	low := variableList[i].Low
	// 	high := variableList[i].High
	// 	middle := variableList[i].Original_base

	// 	variableList[i].Value = tgGen.Get(low, middle, high)

	// 	checkLowMiddleHigh(low, middle, high)
	// 	// fmt.Println(variableList[i].Name)
	// 	// fmt.Println("L M H: ", low, middle, high, " Chosen: ", variableList[i].Value)

	// }

	// fmt.Println("UsbTstSpecificity after:", UsbTstSpecificity)

	// // transition probabilities

}

func checkLowMiddleHigh(low float64, middle float64, high float64) {
	// set at zero, do not vary
	if low == 0 && middle == 0 && high == 0 {
		return
	}
	if high < middle || high < low {
		fmt.Println("problem with high and lows error 1")
		fmt.Println("L M H: ", low, middle, high)
		os.Exit(1)
	}
	if low > middle || low > high {
		fmt.Println("problem with high and lows error 2")
		fmt.Println("L M H: ", low, middle, high)
		os.Exit(1)
	}

}

func beginSingleAnalysis(size string, NumberOfCycles uint, NumberOfIterations uint, SimName string, IsClosedCohort uint) {

	// currently unused

	// cfg := profile.Config{
	// 	CPUProfile: true,
	// 	// MemProfile:     true,
	// 	ProfilePath:    ".",  // store profiles in current directory
	// 	NoShutdownHook: true, // do not hook SIGINT
	// }
	// // p.Stop() must be called before the program exits to
	// // ensure profiling information is written to disk.

	// p := profile.Start(&cfg)

	// SimName = SimName

	// // Hi from LIMCAT
	// show_greeting()

	//// printMemoryUse("Before simluation")

	// // print name of sim
	// fmt.Println("Running simulation: ", SimName)

	// fmt.Println("With this many runs", NumberOfIterations)

	// NumberOfPeopleStartingByYear = make(map[int]uint)
	// NumberOfPeopleEnteringByYear = make(map[int]uint)

	// NumberOfPeopleStartingByYear[2001] = 25534900.0
	// NumberOfPeopleStartingByYear[2014] = 31206652.0

	// NumberOfPeopleEnteringByYear[2001] = 569885.0
	// NumberOfPeopleEnteringByYear[2002] = 526445.0
	// NumberOfPeopleEnteringByYear[2003] = 548132.0
	// NumberOfPeopleEnteringByYear[2004] = 591289.0
	// NumberOfPeopleEnteringByYear[2005] = 619247.0
	// NumberOfPeopleEnteringByYear[2006] = 632620.0
	// NumberOfPeopleEnteringByYear[2007] = 611119.0
	// NumberOfPeopleEnteringByYear[2008] = 577231.0
	// NumberOfPeopleEnteringByYear[2009] = 550541.0
	// NumberOfPeopleEnteringByYear[2010] = 583596.0
	// NumberOfPeopleEnteringByYear[2011] = 569812.0
	// NumberOfPeopleEnteringByYear[2012] = 559316.0
	// NumberOfPeopleEnteringByYear[2013] = 568943.0
	// NumberOfPeopleEnteringByYear[2014] = 564637.0

	// if size == "s" {
	// 	NumberOfPeopleEnteringPerYear = 48
	// 	NumberOfPeopleStarting = 37518
	// } else if size == "m" {
	// 	// NumberOfPeopleEnteringPerYear = 0
	// 	NumberOfPeopleEnteringPerYear = 542
	// 	NumberOfPeopleStarting = 380115
	// } else if size == "l" {
	// 	NumberOfPeopleEnteringPerYear = 5881
	// 	NumberOfPeopleStarting = 3799979
	// }

	// if IsClosedCohort == 1 {
	// 	NumberOfPeopleEnteringPerYear = 0
	// }

	// setEnvironment()

	// // TODO: remove hardcoded cycles
	// NumberOfPeopleEntering = NumberOfPeopleEnteringPerYear * (NumberOfCycles + 1)
	// NumberOfPeople = NumberOfPeopleEntering + NumberOfPeopleStarting

	// RunAdjustment = 30733353.0 / float64(NumberOfPeopleStarting)

	// // these are the totals for the number of people in the "sample" from the
	// // current cohort and the incoming cohort in IPUMS
	// TotalIpumsNew = int(NumberOfPeopleEnteringByYear[2014])
	// TotalIpumsCurrent = int(NumberOfPeopleStartingByYear[2014])

	// fmt.Println("and ", NumberOfPeopleStarting, "initial individuals")
	// fmt.Println("and ", NumberOfPeopleEntering, "individuals entering")
	// fmt.Println("and ", NumberOfPeople, "total")

	// initializeInputs(NumberOfCycles)

	//// printMemoryUse("After inputs initialization")

	// initializeVariables()
	// calculateVariables()

	// Query.setUp()

	// initializeConstants()

	//// printMemoryUse("After query set-up")

	// runInterventions(NumberOfIterations)

	//// printMemoryUse("after simulation")

	// 	mem.Alloc - these are the bytes that were allocated and still in use

	// mem.TotalAlloc - what we allocated throughout the lifetime

	// mem.HeapAlloc - what’s being used on the heap right now

	// mem.HeapSys - this includes what is being used by the heap and what has been reclaimed but not given back out

	// p.Stop()

}

////////////////////////// -------------- Index ------ //////////////////////

func random_int(max uint, personId uint) int {
	random := RandomController.nextShuffle(personId)
	random = random * float64(max)
	return int(random)
}

func setEnvironment() {

	environment := os.Getenv("LIMCATENV")
	if environment == "remote" {
		// set number of cores to max, ie go to 11
		runtime.GOMAXPROCS(runtime.NumCPU())
		fmt.Println("using ", runtime.NumCPU(), " cores")

		fmt.Println(" == on the remote ==")
		DATABASE_PATH = "database/limcat-zero-index.sqlite"

	} else if environment == "laptop" {

		/// set number of cores to max-2, since still need to use the computer!
		runtime.GOMAXPROCS(runtime.NumCPU() - 2)
		fmt.Println("using ", runtime.NumCPU()-2, " cores")

		fmt.Println(" == on the laptop ==")
		DATABASE_PATH = "database/limcat-zero-index.sqlite"

		if RunType == "psa" {
			DATABASE_PATH = "database/limcat-zero-index.sqlite"
			// DATABASE_PATH = "database/limcat-zero-index dec 30 backup.sqlite"
		}

	} else {
		fmt.Println("Cannot determine environment")
		os.Exit(1)
	}

}

func shuffle(chains []Chain, personId uint) []Chain {
	chainsCopy := make([]Chain, len(chains), len(chains))
	//Println("og: ", chains)
	copy(chainsCopy, chains)
	N := len(chainsCopy)
	for i := 0; i < N; i++ {
		// choose index uniformly in [i, N-1]
		r := i + random_int(uint(N-i), personId)
		chainsCopy[r], chainsCopy[i] = chainsCopy[i], chainsCopy[r]
	}
	//fmt.Println("shuffled: ", chainsCopy)
	return chainsCopy
}

// Since we are using an open cohort, we need to add people to the
// simulation every year - these represent people that are being
// born into the simulation
func createNewPeople(cycle Cycle, number uint, mutex *sync.Mutex) {

	//TODO: switch import source

	idForFirstNewPerson := len(Inputs.People)
	currentPersonId := uint(len(Inputs.People))

	// make sure that each iteration-cycle uses the same incoming sample
	rand.Seed(int64(IterationSeed * int(cycle.Id)))

	var numberOfPeopleEnteringThisCycle uint

	var year int
	if RunType == "calib" || RunType == "psa" || RunType == "dsa" {
		year = int(cycle.Year)
	} else {
		year = 2014
	}

	if year > 2014 {
		year = 2014
	}

	numberOfPeopleEnteringThisCycle = AdjustedNumberOfPeopleEnteringPerCycleByYear[year]

	// fmt.Println("Adding this many people:", numberOfPeopleEnteringThisCycle)

	for i := 0; uint(i) < numberOfPeopleEnteringThisCycle; i++ {

		// 568943 is the number of people in the incoming cohort from IPUMS
		// this randomly samples one person from the new people group
		rnd := rand.Intn(int(NumberOfPeopleEnteringByYear[year]))

		baseLineId := Query.Random_sample_new[year][rnd]
		baseInitLine := Inputs.BaseInitLines[baseLineId]

		// make person
		person := Person{currentPersonId, 0, 0, 0, 0, false, 0, 0, false}
		currentPersonId++

		// non-randomized chains to assign
		chainNames := []string{"Sex", "Race", "Age grouping", "Citizen", "Length of time in US", "Birthplace"}
		lineMap := structs.Map(&baseInitLine)

		// to account for spaces
		lineMap["Age grouping"] = lineMap["Age_group"]
		lineMap["Length of time in US"] = lineMap["Years_in_us"]

		for _, chainName := range chainNames {
			// get chain
			chain := Query.getChainByName(chainName)

			// get state
			stateName := lineMap[chainName].(string)
			state := Query.getStateByName(stateName)

			// save
			var mr MasterRecord
			mr.Cycle_id = cycle.Id
			mr.State_id = state.Id
			mr.Chain_id = chain.Id
			mr.Person_id = person.Id
			mr.Has_entered_simulation = true

			// Query.State_id_by_cycle_and_person_and_chain[mr.Cycle_id][mr.Person_id][mr.Chain_id] = mr.State_id
			// fmt.Println(mr.Person_id, mr.Chain_id)
			Query.Master_record_current_cycle_by_person_and_chain[mr.Person_id][mr.Chain_id] = mr

		}
		// asign age through age group

		person.Age = 15.0

		// set their length of time in US (lot)
		lotChain := Query.getChainByName("Length of time in US")
		lotState := person.get_state_by_chain(lotChain, cycle)
		lotStateName := lotState.Name

		if lotStateName == "Less than one year" {
			person.YearsInUs = rand.Float64() // random between 0 and 1
		} else if lotStateName == "Between one and 5 years" {
			person.YearsInUs = 1 + 4*rand.Float64()
		} else if lotStateName == "5 or more years" {
			person.YearsInUs = 6 + 0*rand.Float64() //ensure rand called equal number of times
		}

		//is HCW

		thisRandom := rand.Float64()
		thisProb := 0.0

		birthplaceStateId := Query.Master_record_current_cycle_by_person_and_chain[person.Id][BIRTHPLACE_CHAIN_ID].State_id
		isUsBorn := (birthplaceStateId == US_BIRTHPLACE_ID)

		// race
		switch Inputs.States[Query.Master_record_current_cycle_by_person_and_chain[person.Id][RACE_CHAIN_ID].State_id].Name {

		case "Asian":
			if isUsBorn {
				thisProb = 0.058
			} else {
				thisProb = 0.095
			}
		case "Black":
			if isUsBorn {
				thisProb = 0.056
			} else {
				thisProb = 0.163
			}
		case "Hispanic":
			if isUsBorn {
				thisProb = 0.027

			} else {
				thisProb = 0.030

			}
		case "Other":
			if isUsBorn {
				thisProb = 0.038

			} else {
				thisProb = 0.093

			}
		case "White":
			if isUsBorn {
				thisProb = 0.049

			} else {
				thisProb = 0.070

			}
		}

		if thisRandom < thisProb {
			person.IsHcw = true
		}

		// add person
		Inputs.People = append(Inputs.People, person)

	}

	// randomized chains
	for i := idForFirstNewPerson; i < len(Inputs.People); i++ {

		// place in unitialized state
		person := Inputs.People[i]
		for _, chain := range ReducedChains {
			uninitializedState := chain.get_uninitialized_state()
			var mr MasterRecord
			mr.Cycle_id = cycle.Id
			mr.State_id = uninitializedState.Id
			mr.Chain_id = chain.Id
			mr.Person_id = person.Id
			mr.Has_entered_simulation = true

			Query.Master_record_current_cycle_by_person_and_chain[mr.Person_id][mr.Chain_id] = mr

		}

	}

	generalChan := make(chan uint)

	// move them forward
	for i := idForFirstNewPerson; i < len(Inputs.People); i++ {
		person := Inputs.People[i]
		go initializeOnePerson(cycle, person, generalChan, mutex)
	}

	for i := idForFirstNewPerson; i < len(Inputs.People); i++ {
		chanString := <-generalChan
		_ = i          // to avoid unused warning
		_ = cycle      // to avoid unused warning
		_ = chanString // to avoid unused warning
	}

}

func createInitialPeople(Inputs Input) Input {

	cycle := Inputs.Cycles[0]

	// set the non-randomized demographic

	currentPersonId := 0

	// make sure that each iteration uses the same intitial sample
	rand.Seed(int64(IterationSeed))

	fmt.Println("starting with this many people ", NumberOfPeopleStarting)

	for i := 0; uint(i) < NumberOfPeopleStarting; i++ {

		// 30733353 is the number of people in the incoming cohort from IPUMS
		// this randomly samples one person from the new people group

		var start_year int
		var rnd int
		if RunType == "calib" {
			start_year = 2001
			rnd = rand.Intn(25534900) // can't use NumPeopleStarting because we're using two data sources here
			// we want to sample as many poeple as CA dept of fin says there are, bc we trust that over ipums
			// however, we need to use the ipums number as the ceiling for this random num gen otherwise
			// will just choose the last person over and over. this person is a FB asian, which really messed up
			// the results for a while!!!
		} else {
			start_year = 2014
			rnd = rand.Intn(int(NumberOfPeopleStartingByYear[start_year]))
		}

		baseLineId := Query.Random_sample_current[start_year][rnd]
		baseInitLine := Inputs.BaseInitLines[baseLineId]

		// make person
		person := Person{uint(currentPersonId), 0, 0, 0, 0, false, 0, 0, false}
		currentPersonId++

		// non-randomized chains to assign
		chainNames := []string{"Sex", "Race", "Age grouping", "Citizen", "Length of time in US", "Birthplace"}
		lineMap := structs.Map(&baseInitLine)

		// to account for spaces
		lineMap["Age grouping"] = lineMap["Age_group"]
		lineMap["Length of time in US"] = lineMap["Years_in_us"]

		for _, chainName := range chainNames {

			// get chain
			chain := Query.getChainByName(chainName)

			// get state
			stateName := lineMap[chainName].(string)
			state := Query.getStateByName(stateName)

			// save
			var mr MasterRecord
			mr.State_id = state.Id
			mr.Chain_id = chain.Id
			mr.Person_id = person.Id
			mr.Has_entered_simulation = true

			Query.Master_record_current_cycle_by_person_and_chain[person.Id][chain.Id] = mr

		}

		// set their age
		ageChain := Query.getChainByName("Age grouping")
		ageState := person.get_state_by_chain(ageChain, cycle)
		ageStateName := ageState.Name
		//fmt.Println(ageStateName)
		low := Query.Low_from_age_group[ageStateName]
		high := Query.High_from_age_group[ageStateName]
		if high == 1000 {
			high = 90
		}
		person.Age = float64(low) + rand.Float64()*float64(high-low)

		// set their length of time in US (lot)
		lotChain := Query.getChainByName("Length of time in US")
		lotState := person.get_state_by_chain(lotChain, cycle)
		lotStateName := lotState.Name

		if lotStateName == "Less than one year" {
			person.YearsInUs = rand.Float64()
		} else if lotStateName == "Between one and 5 years" {
			person.YearsInUs = 1 + 4*rand.Float64()
		} else if lotStateName == "5 or more years" {
			person.YearsInUs = 6 + 0*rand.Float64() //ensure rand called equal number of times
		}

		//is HCW

		thisRandom := rand.Float64()
		thisProb := 0.0

		birthplaceStateId := Query.Master_record_current_cycle_by_person_and_chain[person.Id][BIRTHPLACE_CHAIN_ID].State_id
		isUsBorn := (birthplaceStateId == US_BIRTHPLACE_ID)

		// race
		switch Inputs.States[Query.Master_record_current_cycle_by_person_and_chain[person.Id][RACE_CHAIN_ID].State_id].Name {

		case "Asian":
			if isUsBorn {
				thisProb = 0.058
			} else {
				thisProb = 0.095
			}
		case "Black":
			if isUsBorn {
				thisProb = 0.056
			} else {
				thisProb = 0.163
			}
		case "Hispanic":
			if isUsBorn {
				thisProb = 0.027

			} else {
				thisProb = 0.030

			}
		case "Other":
			if isUsBorn {
				thisProb = 0.038

			} else {
				thisProb = 0.093

			}
		case "White":
			if isUsBorn {
				thisProb = 0.049

			} else {
				thisProb = 0.070

			}
		}

		if thisRandom < thisProb {
			person.IsHcw = true
		}

		// add person
		Inputs.People = append(Inputs.People, person)
		//fmt.Println(person.Age)

	}

	fmt.Println("now working on randomized chains")

	for _, person := range Inputs.People {
		for _, chain := range ReducedChains {
			uninitializedState := chain.get_uninitialized_state()
			var mr MasterRecord
			mr.State_id = uninitializedState.Id
			mr.Chain_id = chain.Id
			mr.Person_id = person.Id
			mr.Has_entered_simulation = true

			Query.Master_record_current_cycle_by_person_and_chain[person.Id][chain.Id] = mr

		}
	}

	return Inputs

}

func adjust_transitions(theseTPs []TransitionProbability, interaction Interaction, cycle Cycle, person Person) []TransitionProbability {

	adjustmentFactor := interaction.Adjustment

	//	fmt.Println(adjustmentFactor)

	for i, _ := range theseTPs {
		// & represents the address, so now tp is a pointer - needed because you want to change the
		// underlying value of the elements of theseTPs, not just a copy of them.
		// note however, that this function as a whole has only a copy of the TPs,
		// we're not modifying the underlying "Inputs"-level TPs.
		tp := &theseTPs[i]
		originalTpBase := tp.Tp_base
		if tp.From_state_id == interaction.From_state_id && tp.To_state_id == interaction.To_state_id {
			tp.Tp_base = tp.Tp_base * adjustmentFactor
			if tp.Tp_base > 1 {
				tp.Tp_base = 1
			}

			if tp.Tp_base == originalTpBase && adjustmentFactor != 1 && originalTpBase != 0 {
				//fmt.Println("Error adjusting TP: ", tp.Id)
				//os.Exit(1)
			}
		}
	}

	return theseTPs
}

func adjust_tps_over_one(theseTPs []TransitionProbability) []TransitionProbability {

	/*
		now, we need to make sure everything adds to one. to do so, we find what
		it currently sums to, and remove the "excess" from the chance of
		staying in the same state ("recursive tp") for example, if a risk factor made
		disease X 1.5 more likely, then the sum of the TPs will add to > 1 after
		adjustment. So, we would take the excess (1 - sum), and remove that from
		the chance of staying the same state (we call this the "recursive tp")

		However, for tunnel states (where they will never stay in the same state
		for multiple cycles), we need a different system.

		There are some tunnels that have recursive TPs left over from the way
		python calculates this (the python scripts down know which intervention
		is activated, etc, so can't know what tunnel/recursive tp is used). We
		need to zero the rescursive TP for tunnel states.
	*/

	// if tunnel, remove recursive tp
	tp := theseTPs[0]
	from_state_id := tp.From_state_id
	fromState := Inputs.States[from_state_id]
	isTunnel := fromState.Is_tunnel

	if isTunnel {
		for i, _ := range theseTPs {
			tp := &theseTPs[i] // need pointer to get underlying value
			// find recursive tp
			if tp.From_state_id == tp.To_state_id {
				tp.Tp_base = 0
			}
		}

	}

	sum := get_sum(theseTPs)
	//fmt.Println("sum of all TPs after adjusting this interaction", sum)
	remain := sum - 1.0
	//fmt.Println("What remains after subtracting 1.0 from the sum", remain)

	// determine whether tunnel

	if isTunnel {

		tunnelTargetId := fromState.Tunnel_target_id
		for i, _ := range theseTPs {
			tp := &theseTPs[i] // need pointer to get underlying value, see above
			//find "tunnel" tp, ie chance of staying in same state
			if tunnelTargetId == tp.To_state_id {
				tp.Tp_base -= remain

				if tp.Tp_base < 0 && (RunType == "psa" || RunType == "dsa") {
					tp.Tp_base = 0
					fmt.Println("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
					fmt.Println("Warning: Tp was under 0")
					fmt.Println("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
					fmt.Println("Corrected to zero")
				}
				if tp.Tp_base < 0.0 {

					fmt.Println("remainign was ", remain)
					fmt.Println("is ", tp.Tp_base)
					fmt.Println(theseTPs)

					tp.Tp_base = 0
					fmt.Println("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
					fmt.Println("Warning: Tp was under 0.")
					fmt.Println("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
					fmt.Println("Corrected to zero")

				}
			}
		}

	} else { // is not tunnel

		for i, _ := range theseTPs {
			tp := &theseTPs[i] // need pointer to get underlying value, see above
			//find "recursive" tp, ie chance of staying in same state
			if tp.From_state_id == tp.To_state_id {
				if tp.Tp_base-remain < 0 {
					fmt.Println("before adjustment ", tp.Tp_base)
				}

				tp.Tp_base = tp.Tp_base - remain

				if tp.Tp_base < 0 && (RunType == "psa" || RunType == "dsa") {
					tp.Tp_base = 0
					fmt.Println("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
					fmt.Println("Warning: Tp was under 0.")
					fmt.Println("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
					fmt.Println("Corrected to zero")
				}
				if tp.Tp_base < 0.0 {
					// TODO: remove

					fmt.Println("remainign was ", remain)
					fmt.Println("is ", tp.Tp_base)
					fmt.Println(theseTPs)

					tp.Tp_base = 0
					fmt.Println("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
					fmt.Println("Warning: Tp was under 0.")
					fmt.Println("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
					fmt.Println("Corrected to zero")

					//fmt.Println(theseTPs)
					//os.Exit(1)
				}
			}
		}

		//check to make sure that people don't stay unitialized
		// TODO: Check for uninitialized 2 [Issue: https://github.com/alexgoodell/go-mdism/issues/43]
		// chain := Inputs.Chains[interaction.Effected_chain_id]
		// unitState := chain.get_uninitialized_state()
		// if theseTPs[0].From_state_id == unitState.Id && recursiveTp != 0 {
		// 	fmt.Println("recursiveTp is not zero for initialization!")
		// 	os.Exit(1)
		// }

	} // end not tunnel

	// This is still a change that they will not sum to one, even if the recursive/tunnel
	// is set to zero. If that is true, the adjust them all up/down to make them sum
	// to one
	sum = get_sum(theseTPs)
	if !equalFloat(sum, 1.0, 0.000001) {
		fmt.Println("Still over one, using second adjustment strategy. Sum was ", sum, theseTPs)
		adjustment := 1.0 / sum
		for i, _ := range theseTPs {
			tp := &theseTPs[i] //
			tp.Tp_base = tp.Tp_base * adjustment
		}
	}

	return theseTPs
}

func show_greeting() {

	// 	greeting := `

	// 	     ██╗      ██╗  ███╗   ███╗   ██████╗   █████╗   ████████╗
	// 	     ██║      ██║  ████╗ ████║  ██╔════╝  ██╔══██╗  ╚══██╔══╝
	// 	     ██║      ██║  ██╔████╔██║  ██║       ███████║     ██║
	// 	     ██║      ██║  ██║╚██╔╝██║  ██║       ██╔══██║     ██║
	// 	     ███████╗ ██║  ██║ ╚═╝ ██║  ╚██████╗  ██║  ██║     ██║
	// 	     ╚══════╝ ╚═╝  ╚═╝     ╚═╝   ╚═════╝  ╚═╝  ╚═╝     ╚═╝

	// 	Modeling TB in California using locally-interacting Markov models
	// `

	// 	// greeting = ansi.Color(greeting, "blue+bh")
	// 	fmt.Println(greeting)

}

func check_sum(theseTPs []TransitionProbability, msg string) {
	sum := get_sum(theseTPs)

	if !equalFloat(sum, 1.0, 0.000001) {
		fmt.Println("sum does not equal 1 !", Inputs.States[theseTPs[0].From_state_id].Name, Inputs.States[theseTPs[0].To_state_id].Name)
		fmt.Println(msg)
		fmt.Println(sum)
		fmt.Println(theseTPs)
		//fmt.Printf("%+v", theseTPs)
		// TODO: re-implement
		os.Exit(1)
	}
}

func get_sum(theseTPs []TransitionProbability) float64 {
	sum := float64(0.0)
	for _, tp := range theseTPs {
		sum += tp.Tp_base
	}
	return sum
}

// EqualFloat() returns true if x and y are approximately equal to the
// given limit. Pass a limit of -1 to get the greatest accuracy the machine
// can manage.
func equalFloat(x float64, y float64, limit float64) bool {

	if limit <= 0.0 {
		limit = math.SmallestNonzeroFloat64
	}

	return math.Abs(x-y) <= (limit * math.Min(math.Abs(x), math.Abs(y)))
}

func pause() {
	time.Sleep(10000000000)
}

// Using  the final transition probabilities, pickState assigns a new state to
// a person. It is given many states and returns one.
func pickStateAndTp(tPs []TransitionProbability, random float64) (State, TransitionProbability) {
	probs := make([]float64, len(tPs), len(tPs))
	for i, tP := range tPs {
		probs[i] = tP.Tp_base
	}

	chosenIndex := pick(probs, random)
	stateId := tPs[chosenIndex].To_state_id
	if stateId == 0 {
		fmt.Println("error!! ")
		os.Exit(1)
	}

	state := get_state_by_id(stateId)
	tp := tPs[chosenIndex]

	if &state != nil {
		return state, tp
	} else {
		fmt.Println("cannot pick state with pickState")
		os.Exit(1)
		return state, tp
	}

}

func tempFixTpsToSumOne(probabilities []float64) []float64 {
	sum := 0.0
	for _, tp := range probabilities {
		sum += tp
	}

	adj := 1.0 / sum
	for i, tp := range probabilities {
		probabilities[i] = tp * adj
	}

	return probabilities

}

// iterates over array of potential states and uses a random value to find
// where new state is. returns new state id.
func pick(probabilities []float64, random float64) int {

	probabilities = tempFixTpsToSumOne(probabilities)

	sum := float64(0.0)
	for i, prob := range probabilities { //for i := 0; i < len(probabilities); i++ {
		sum += prob
		if random <= sum {
			return i
		}
	}
	// TODO: Add error report here [Issue: https://github.com/alexgoodell/go-mdism/issues/4]
	fmt.Println("problem with pick")
	fmt.Println(probabilities)
	os.Exit(1)
	return 0
}

//////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////

func (Query *Query_t) setUp() {

	fmt.Println("setting up query")

	// --------------- sampling mechanism --------------------

	// ------- current

	years_list := []int{2001, 2014}

	Query.Random_sample_current = make(map[int][]uint)

	for _, year := range years_list {
		Query.Random_sample_current[year] = make([]uint, NumberOfPeopleStartingByYear[year], NumberOfPeopleStartingByYear[year])
		z := 0
		for i := 0; i < len(Inputs.BaseInitLines); i++ {
			var weight uint
			if year == 2001 {
				weight = Inputs.BaseInitLines[i].Weight2001
			} else if year == 2014 {
				weight = Inputs.BaseInitLines[i].Weight2014
			}
			// fmt.Println(weight)
			for r := 0; uint(r) < weight; r++ {
				// fmt.Println(r, i, z)
				Query.Random_sample_current[year][z] = uint(i)
				z++
			}
		}

	}

	fmt.Println("Total number of people to sample from in 2001", len(Query.Random_sample_current[2001]))
	fmt.Println("Total number of people to sample from in 2014", len(Query.Random_sample_current[2014]))

	// ------- new (incoming)

	// Mechanism to sample from "new" population (ie, individuals aging into
	// the model or immigrating into CA)

	// Mechanism to sample from current population

	years_list = []int{2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014}

	Query.Random_sample_new = make(map[int][]uint)

	for _, year := range years_list {
		Query.Random_sample_new[year] = make([]uint, NumberOfPeopleEnteringByYear[year], NumberOfPeopleEnteringByYear[year])
		z := 0
		for i := 0; i < len(Inputs.BaseInitLines); i++ {
			var weight uint
			if year == 2001 {
				weight = Inputs.BaseInitLines[i].WeightNewPeople2001
			} else if year == 2002 {
				weight = Inputs.BaseInitLines[i].WeightNewPeople2002
			} else if year == 2003 {
				weight = Inputs.BaseInitLines[i].WeightNewPeople2003
			} else if year == 2004 {
				weight = Inputs.BaseInitLines[i].WeightNewPeople2004
			} else if year == 2005 {
				weight = Inputs.BaseInitLines[i].WeightNewPeople2005
			} else if year == 2006 {
				weight = Inputs.BaseInitLines[i].WeightNewPeople2006
			} else if year == 2007 {
				weight = Inputs.BaseInitLines[i].WeightNewPeople2007
			} else if year == 2008 {
				weight = Inputs.BaseInitLines[i].WeightNewPeople2008
			} else if year == 2009 {
				weight = Inputs.BaseInitLines[i].WeightNewPeople2009
			} else if year == 2010 {
				weight = Inputs.BaseInitLines[i].WeightNewPeople2010
			} else if year == 2011 {
				weight = Inputs.BaseInitLines[i].WeightNewPeople2011
			} else if year == 2012 {
				weight = Inputs.BaseInitLines[i].WeightNewPeople2012
			} else if year == 2013 {
				weight = Inputs.BaseInitLines[i].WeightNewPeople2013
			} else if year == 2014 {
				weight = Inputs.BaseInitLines[i].WeightNewPeople2014
			}
			// fmt.Println(year, weight)
			for r := 0; uint(r) < weight; r++ {
				// fmt.Println(r, i, z)
				Query.Random_sample_new[year][z] = uint(i)
				z++
			}
		}

	}

	fmt.Println("Total number of new people to sample from in 2001", len(Query.Random_sample_new[2001]))
	fmt.Println("Total number of new people to sample from in 2002", len(Query.Random_sample_new[2002]))
	fmt.Println("Total number of new people to sample from in 2003", len(Query.Random_sample_new[2003]))
	fmt.Println("Total number of new people to sample from in 2004", len(Query.Random_sample_new[2004]))
	fmt.Println("Total number of new people to sample from in 2005", len(Query.Random_sample_new[2005]))
	fmt.Println("Total number of new people to sample from in 2006", len(Query.Random_sample_new[2006]))
	fmt.Println("Total number of new people to sample from in 2007", len(Query.Random_sample_new[2007]))
	fmt.Println("Total number of new people to sample from in 2008", len(Query.Random_sample_new[2008]))
	fmt.Println("Total number of new people to sample from in 2009", len(Query.Random_sample_new[2009]))
	fmt.Println("Total number of new people to sample from in 2010", len(Query.Random_sample_new[2010]))
	fmt.Println("Total number of new people to sample from in 2011", len(Query.Random_sample_new[2011]))
	fmt.Println("Total number of new people to sample from in 2012", len(Query.Random_sample_new[2012]))
	fmt.Println("Total number of new people to sample from in 2013", len(Query.Random_sample_new[2013]))
	fmt.Println("Total number of new people to sample from in 2014", len(Query.Random_sample_new[2014]))

	// ------------------------- Calibration tracker system

	years := []string{"2000", "2001", "2002", "2003", "2004", "2005", "2006", "2007", "2008", "2009", "2010", "2011", "2012", "2013", "2014"}

	// Query.OutputYears = make([]OutputYear)

	groups := []string{"Total", "Homeless", "HIV", "Diabetes", "ESRD", "Smokers", "Transplant", "TNF-alpha", "Asian", "Black", "Hispanic", "Other", "White", "Male", "Female"}

	nativity := []string{"FB", "USB"}

	Query.Iteration_year_group = make([]map[string]map[string]map[string]float64, int(NumberOfIterations), int(NumberOfIterations))
	for i := 0; i < int(NumberOfIterations); i++ {
		Query.Iteration_year_group[i] = make(map[string]map[string]map[string]float64)
		for y := 0; y < len(years); y++ {
			Query.Iteration_year_group[i][years[y]] = make(map[string]map[string]float64)
			for g := 0; g < len(groups); g++ {
				Query.Iteration_year_group[i][years[y]][groups[g]] = make(map[string]float64)
				for n := 0; n < len(nativity); n++ {
					Query.Iteration_year_group[i][years[y]][groups[g]][nativity[n]] = 0
				}
			}

		}

	}

	// transmission dynamics
	numberOfCalculatedCycles := len(Inputs.Cycles)

	Query.LTBI_risk_by_cycle_isUsb_and_race = make([][][]float64, numberOfCalculatedCycles, numberOfCalculatedCycles)
	Query.Num_active_cases_by_cycle_isUsb_and_race = make([][][]float64, numberOfCalculatedCycles, numberOfCalculatedCycles)
	Query.Num_susceptible_by_cycle_isUsb_and_race = make([][][]uint, numberOfCalculatedCycles, numberOfCalculatedCycles)
	Query.Total_susceptible_by_cycle = make([]uint, numberOfCalculatedCycles, numberOfCalculatedCycles)
	Query.Total_active_by_cycle = make([]float64, numberOfCalculatedCycles, numberOfCalculatedCycles)

	for i := 0; i < numberOfCalculatedCycles; i++ {
		Query.LTBI_risk_by_cycle_isUsb_and_race[i] = make([][]float64, 2, 2)
		Query.Num_active_cases_by_cycle_isUsb_and_race[i] = make([][]float64, 2, 2)
		Query.Num_susceptible_by_cycle_isUsb_and_race[i] = make([][]uint, 2, 2)
		for p := 0; p < 2; p++ {
			Query.LTBI_risk_by_cycle_isUsb_and_race[i][p] = make([]float64, len(Inputs.States), len(Inputs.States))
			Query.Num_active_cases_by_cycle_isUsb_and_race[i][p] = make([]float64, len(Inputs.States), len(Inputs.States))
			Query.Num_susceptible_by_cycle_isUsb_and_race[i][p] = make([]uint, len(Inputs.States), len(Inputs.States))
			for q := 0; q < len(Inputs.States); q++ {
				Query.LTBI_risk_by_cycle_isUsb_and_race[i][p][q] = 0
				Query.Num_active_cases_by_cycle_isUsb_and_race[i][p][q] = 0
				Query.Num_susceptible_by_cycle_isUsb_and_race[i][p][q] = 0
			}
		}
	}

	Query.Total_population_by_cycle = make([]uint, numberOfCalculatedCycles, numberOfCalculatedCycles)
	Query.Total_population_by_cycle[0] = NumberOfPeopleStarting
	//fmt.Println("starting pop with", Query.Total_population_by_cycle[0])

	Query.State_populations_by_cycle = make([][]uint, numberOfCalculatedCycles, numberOfCalculatedCycles)
	for i := 0; i < len(Inputs.Cycles); i++ {
		Query.State_populations_by_cycle[i] = make([]uint, len(Inputs.States), len(Inputs.States))
	}

	Query.Low_from_age_group = make(map[string]uint)
	Query.High_from_age_group = make(map[string]uint)

	Query.Low_from_age_group["Age 15-19"] = 15
	Query.Low_from_age_group["Age 20-24"] = 20
	Query.Low_from_age_group["Age 25-29"] = 25
	Query.Low_from_age_group["Age 30-34"] = 30
	Query.Low_from_age_group["Age 35-39"] = 35
	Query.Low_from_age_group["Age 40-44"] = 40
	Query.Low_from_age_group["Age 45-49"] = 45
	Query.Low_from_age_group["Age 50-54"] = 50
	Query.Low_from_age_group["Age 55-59"] = 55
	Query.Low_from_age_group["Age 60-64"] = 60
	Query.Low_from_age_group["Age 65-69"] = 65
	Query.Low_from_age_group["Age 70-74"] = 70
	Query.Low_from_age_group["Age 75-79"] = 75
	Query.Low_from_age_group["Age 80+"] = 80

	Query.High_from_age_group["Age 15-19"] = 19
	Query.High_from_age_group["Age 20-24"] = 24
	Query.High_from_age_group["Age 25-29"] = 29
	Query.High_from_age_group["Age 30-34"] = 34
	Query.High_from_age_group["Age 35-39"] = 39
	Query.High_from_age_group["Age 40-44"] = 44
	Query.High_from_age_group["Age 45-49"] = 49
	Query.High_from_age_group["Age 50-54"] = 54
	Query.High_from_age_group["Age 55-59"] = 59
	Query.High_from_age_group["Age 60-64"] = 64
	Query.High_from_age_group["Age 65-69"] = 69
	Query.High_from_age_group["Age 70-74"] = 74
	Query.High_from_age_group["Age 75-79"] = 79
	Query.High_from_age_group["Age 80+"] = 1000

	//life expectancy

	Query.Life_expectancy_by_sex_and_age = make(map[string]map[string]float64)
	Query.Life_expectancy_by_sex_and_age["Male"] = make(map[string]float64)
	Query.Life_expectancy_by_sex_and_age["Female"] = make(map[string]float64)

	Query.Life_expectancy_by_sex_and_age["Male"]["Age 15-19"] = 719.270144
	Query.Life_expectancy_by_sex_and_age["Male"]["Age 20-24"] = 662.4758652
	Query.Life_expectancy_by_sex_and_age["Male"]["Age 25-29"] = 606.7263791
	Query.Life_expectancy_by_sex_and_age["Male"]["Age 30-34"] = 550.785185
	Query.Life_expectancy_by_sex_and_age["Male"]["Age 35-39"] = 494.9424896
	Query.Life_expectancy_by_sex_and_age["Male"]["Age 40-44"] = 439.5876716
	Query.Life_expectancy_by_sex_and_age["Male"]["Age 45-49"] = 385.7835031
	Query.Life_expectancy_by_sex_and_age["Male"]["Age 50-54"] = 334.3182061
	Query.Life_expectancy_by_sex_and_age["Male"]["Age 55-59"] = 285.5997125
	Query.Life_expectancy_by_sex_and_age["Male"]["Age 60-64"] = 239.1646958
	Query.Life_expectancy_by_sex_and_age["Male"]["Age 65-69"] = 194.9921972
	Query.Life_expectancy_by_sex_and_age["Male"]["Age 70-74"] = 154.3657379
	Query.Life_expectancy_by_sex_and_age["Male"]["Age 75-79"] = 117.9608694
	Query.Life_expectancy_by_sex_and_age["Male"]["Age 80+"] = 70.40400821
	Query.Life_expectancy_by_sex_and_age["Female"]["Age 15-19"] = 774.8942068
	Query.Life_expectancy_by_sex_and_age["Female"]["Age 20-24"] = 716.2180218
	Query.Life_expectancy_by_sex_and_age["Female"]["Age 25-29"] = 657.8525842
	Query.Life_expectancy_by_sex_and_age["Female"]["Age 30-34"] = 599.8731683
	Query.Life_expectancy_by_sex_and_age["Female"]["Age 35-39"] = 542.3026273
	Query.Life_expectancy_by_sex_and_age["Female"]["Age 40-44"] = 485.4336343
	Query.Life_expectancy_by_sex_and_age["Female"]["Age 45-49"] = 429.7964009
	Query.Life_expectancy_by_sex_and_age["Female"]["Age 50-54"] = 375.773572
	Query.Life_expectancy_by_sex_and_age["Female"]["Age 55-59"] = 323.3618636
	Query.Life_expectancy_by_sex_and_age["Female"]["Age 60-64"] = 272.4274385
	Query.Life_expectancy_by_sex_and_age["Female"]["Age 65-69"] = 223.9226282
	Query.Life_expectancy_by_sex_and_age["Female"]["Age 70-74"] = 178.7898474
	Query.Life_expectancy_by_sex_and_age["Female"]["Age 75-79"] = 137.9313511
	Query.Life_expectancy_by_sex_and_age["Female"]["Age 80+"] = 79.59861007

	// syncornizations
	Query.Synchronization_to_states_by_trigger_state = make([][]uint, len(Inputs.States), len(Inputs.States))
	for i := 0; i < len(Inputs.States); i++ {
		//empty now but filled in below
		Query.Synchronization_to_states_by_trigger_state[i] = make([]uint, 0)
	}

	for _, synchronization := range Inputs.Synchronizations {
		Query.Synchronization_to_states_by_trigger_state[synchronization.Trigger_state_id] = append(Query.Synchronization_to_states_by_trigger_state[synchronization.Trigger_state_id], synchronization.To_state_id)
	}

	// Get ID of Inputs.TransitionProbabilitiesByStratum by transition prob ID and stratum ID
	//Query.Tp_stratum_id_by_tp_and_stratum[transitionProbability.Id][stratum_id]
	Query.Tp_stratum_id_by_tp_and_stratum = make([][]uint, len(Inputs.TransitionProbabilities), len(Inputs.TransitionProbabilities))
	for i := 0; i < len(Inputs.TransitionProbabilities); i++ {
		Query.Tp_stratum_id_by_tp_and_stratum[i] = make([]uint, len(Inputs.Strata), len(Inputs.Strata))
	}
	for _, tpbs := range Inputs.TransitionProbabilitiesByStratum {
		//fmt.Println(tpbs.Transition_probability_id, tpbs.Stratum_id)
		Query.Tp_stratum_id_by_tp_and_stratum[tpbs.Transition_probability_id][tpbs.Stratum_id] = tpbs.Id
	}

	// Stratum id by stratum_hash (which is a string listing all)
	// the states (ex: 23.21.35.21, etc). Unique to each stratum.
	Query.Stratum_id_by_hash = make(map[string]uint)
	for _, stratum := range Inputs.Strata {
		Query.Stratum_id_by_hash[stratum.Stratum_hash] = stratum.Id
	}

	Query.Chain_ids_by_stratum_type_id = make([][]uint, len(Inputs.StratumTypes), len(Inputs.StratumTypes))
	for i := 0; i < len(Inputs.StratumTypes); i++ {
		// initially empty, will append the correct chains onto this slice
		Query.Chain_ids_by_stratum_type_id[i] = make([]uint, 0)
	}

	for _, stratumTypeContent := range Inputs.StratumTypeContents {
		stId := stratumTypeContent.Stratum_type_id
		Query.Chain_ids_by_stratum_type_id[stId] = append(Query.Chain_ids_by_stratum_type_id[stId], stratumTypeContent.Chain_id)
	}

	// Uninitialized
	Query.Unintialized_state_by_chain = make([]uint, len(Inputs.Chains), len(Inputs.Chains))
	for _, state := range Inputs.States {
		if state.Is_uninitialized_state == true {
			Query.Unintialized_state_by_chain[state.Chain_id] = state.Id
		}
	}

	// Query.Life_expectancy_by_sex_and_age = make(map[SexAge]float64)

	// for _, lifeExpectancy := range Inputs.LifeExpectancies {
	// 	key := SexAge{lifeExpectancy.Sex_state_id, lifeExpectancy.Age_state_id}
	// 	Query.Life_expectancy_by_sex_and_age[key] = lifeExpectancy.Life_expectancy
	// }

	Query.chain_id_by_name = make(map[string]uint)
	for _, chain := range Inputs.Chains {
		Query.chain_id_by_name[chain.Name] = chain.Id
	}

	Query.state_id_by_name = make(map[string]uint)
	for _, state := range Inputs.States {
		Query.state_id_by_name[state.Name] = state.Id
	}

	// Query.State_id_by_cycle_and_person_and_chain = make([][][]uint, len(Inputs.Cycles)+1, len(Inputs.Cycles)+1)
	// for i, _ := range Query.State_id_by_cycle_and_person_and_chain {
	// 	//People
	// 	Query.State_id_by_cycle_and_person_and_chain[i] = make([][]uint, NumberOfPeople, NumberOfPeople)
	// 	for p, _ := range Query.State_id_by_cycle_and_person_and_chain[i] {
	// 		Query.State_id_by_cycle_and_person_and_chain[i][p] = make([]uint, len(Inputs.Chains), len(Inputs.Chains))
	// 	}
	// }

	//Cycles
	//Query.States_ids_by_cycle_and_person = make([][]uint, 1000000, 1000000)

	Query.Tps_by_from_state = make([][]TransitionProbability, len(Inputs.States), len(Inputs.States))
	for _, transitionProbability := range Inputs.TransitionProbabilities {
		Query.Tps_by_from_state[transitionProbability.From_state_id] = append(Query.Tps_by_from_state[transitionProbability.From_state_id], transitionProbability)
	}

	// make structure
	Query.Tp_id_by_from_state_and_to_state = make([][]uint, len(Inputs.States), len(Inputs.States))
	for i := 0; i < len(Inputs.States); i++ {
		Query.Tp_id_by_from_state_and_to_state[i] = make([]uint, len(Inputs.States), len(Inputs.States))
	}

	// fill structure
	for _, tp := range Inputs.TransitionProbabilities {
		Query.Tp_id_by_from_state_and_to_state[tp.From_state_id][tp.To_state_id] = tp.Id
	}

	Query.interaction_ids_by_in_state_and_from_state = make(map[InteractionKey][]uint)
	for _, interaction := range Inputs.Interactions {
		var interactionKey InteractionKey
		interactionKey.From_state_id = interaction.From_state_id
		interactionKey.In_state_id = interaction.In_state_id
		Query.interaction_ids_by_in_state_and_from_state[interactionKey] = append(Query.interaction_ids_by_in_state_and_from_state[interactionKey], interaction.Id)
	}

	//fmt.Println(Query.interaction_ids_by_in_state_and_from_state)

	Query.Chain_id_by_state = make([]uint, len(Inputs.States), len(Inputs.States))

	for _, state := range Inputs.States {
		Query.Chain_id_by_state[state.Id] = state.Chain_id
	}

	// ############## Other death state by chain id ##################

	Query.Death_state_by_chain = make([]uint, len(Inputs.Chains), len(Inputs.Chains))
	for _, chain := range Inputs.Chains {
		// find other death state by iteration
		deathState := State{}
		for _, state := range Inputs.States {
			if state.Is_death_state && state.Chain_id == chain.Id {
				deathState = state
			}
		}

		if !deathState.Is_death_state {
			fmt.Println("Problem finding other death state for chain", chain.Id)
			os.Exit(1)
		}

		Query.Death_state_by_chain[chain.Id] = deathState.Id

	}

	// ############## Costs by state id ##################

	// fill in structure of query data with blanks
	Query.Cost_by_state_id = make([]float64, len(Inputs.States), len(Inputs.States))
	for i := 0; i < len(Inputs.States); i++ {
		Query.Cost_by_state_id[i] = 0
	}

	// put input from costs.csv (stored in Inputs.Costs) to fill in query data
	for _, cost := range Inputs.Costs {
		Query.Cost_by_state_id[cost.State_id] = cost.Costs
	}

	// ############## Disability weights by state id ##################

	// fill in structure of query data with blanks
	Query.Disability_weight_by_state_id = make([]float64, len(Inputs.States), len(Inputs.States))
	for i := 0; i < len(Inputs.States); i++ {
		Query.Disability_weight_by_state_id[i] = 0
	}

	// put input from costs.csv (stored in Inputs.Costs) to fill in query data
	for _, dw := range Inputs.DisabilityWeights {
		Query.Disability_weight_by_state_id[dw.State_id] = dw.Disability_weight
	}

	// Outputs
	Outputs.OutputsByCycle = make([]OutputByCycle, numberOfCalculatedCycles, numberOfCalculatedCycles)
	Query.Outputs_id_by_cycle_and_state = make([][]uint, numberOfCalculatedCycles, numberOfCalculatedCycles)
	Outputs.OutputsByCycleStateFull = make([]OutputByCycleState, numberOfCalculatedCycles*len(Inputs.States), numberOfCalculatedCycles*len(Inputs.States))

	i := 0
	for c := 0; c < numberOfCalculatedCycles; c++ {
		Query.Outputs_id_by_cycle_and_state[c] = make([]uint, len(Inputs.States), len(Inputs.States))
		for s, state := range Inputs.States {
			var outputCS OutputByCycleState
			outputCS.Id = uint(i)
			outputCS.State_id = uint(s)
			outputCS.Cycle_id = uint(c)
			outputCS.Year = Inputs.Cycles[c].Year
			outputCS.Chain_id = state.Chain_id
			outputCS.Population = 0
			outputCS.Intervention_id = InterventionId
			outputCS.Intervention_name = Inputs.Interventions[InterventionId].Name
			outputCS.State_name = state.Name
			Outputs.OutputsByCycleStateFull[i] = outputCS

			Query.Outputs_id_by_cycle_and_state[c][s] = uint(i)
			i++
		}
	}

	Query.Has_interaction_by_state_id = make([]bool, len(Inputs.States), len(Inputs.States))
	for _, interaction := range Inputs.Interactions {
		Query.Has_interaction_by_state_id[interaction.From_state_id] = true
	}

	Query.State_id_has_stratified_tp = make([]bool, len(Inputs.States), len(Inputs.States))
	for _, transitionProbability := range Inputs.TransitionProbabilities {
		if transitionProbability.Is_stratified {
			Query.State_id_has_stratified_tp[transitionProbability.From_state_id] = true
		}
	}

}

/////////////// ------------------ random controller ------------ //////////

type RandomController_t struct {
	randomListShuffle []float64 // this is a slice of random variables
	// randomListCPM        [][][]float64 // this is a slice of random variables
	randomListP          [][]float64 // this is a slice of random variables
	randomListPM         [][]float64 // this is a slice of random variables
	accessCounterCPM     int         //this is a counter for how many times a random number was generated
	accessCounterShuffle uint
}

func (RandomController *RandomController_t) initialize(cycleId uint) {

	// fmt.Println("Reseeding random data")
	// rand.Seed(int64(IterationNum*1000 + cycleId)) //time.Now().UTC().UnixNano()

	// "sister" iterations will use identical numbers

	// makes sure that each psa-iteration-cycle uses the same values
	if RunType == "psa" || RunType == "calib" {
		// this ONLY WORKS FOR SINGLE PSA, SINGLE ITERATION. Otherwise use IterationNum*10000 + uint(PsaRunNum)*1000
		newSeed := int64(TheSeed + int64(cycleId))
		// fmt.Println("Reseeding random data with seed of ", newSeed)
		rand.Seed(newSeed)
	}

	// fmt.Println("sizes:", len(Inputs.Cycles), NumberOfPeople, len(Inputs.Chains), 4)

	RandomController.randomListPM = make([][]float64, NumberOfPeople, NumberOfPeople)
	for p := 0; uint(p) < NumberOfPeople; p++ {
		RandomController.randomListPM[p] = make([]float64, len(Inputs.Chains), len(Inputs.Chains))
		for m := range Inputs.Chains {
			RandomController.randomListPM[p][m] = rand.Float64()
		}
	}
}

func (RandomController *RandomController_t) initializeRandomListShuffle() {
	RandomController.randomListShuffle = make([]float64, NumberOfPeople, NumberOfPeople)
	for p := 0; uint(p) < NumberOfPeople; p++ {
		RandomController.randomListShuffle[p] = rand.Float64()
	}
}

func (RandomController *RandomController_t) resetCounters() {
	RandomController.accessCounterCPM = 0
	RandomController.accessCounterShuffle = 0
}

func (RandomController *RandomController_t) nextShuffle(person_id uint) float64 {

	// can turn off after debugging
	// mutex.Lock()
	// RandomController.accessCounterShuffle++
	// mutex.Unlock()

	return RandomController.randomListShuffle[person_id]
}

func (RandomController *RandomController_t) nextPM(personId uint, chainId uint) float64 {
	return RandomController.randomListPM[personId][chainId]

}

func (RandomController *RandomController_t) getShuffleCounter(mutex *sync.Mutex) uint {

	mutex.Lock()
	count := RandomController.accessCounterShuffle
	mutex.Unlock()

	return count
}

func (RandomController *RandomController_t) getCPMCounter(mutex *sync.Mutex) uint {

	mutex.Lock()
	count := RandomController.accessCounterCPM
	mutex.Unlock()

	return uint(count)
}

func hash(s string) int64 {
	h := fnv.New32a()
	h.Write([]byte(s))

	p := int64(h.Sum32())
	// fmt.Println(s, ":", p)
	// pause()
	return p
}

func print(msg string) {
	fmt.Println()
	fmt.Print(msg)
}

func printComplete() {
	fmt.Print("complete")
}

var letters = []rune("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")

func randSeq(n uint) string {
	b := make([]rune, n)
	for i := range b {
		b[i] = letters[rand.Intn(len(letters))]
	}
	return string(b)
}

func blankMasterRecordsSet() [][]MasterRecord {

	mrSet := make([][]MasterRecord, NumberOfPeople, NumberOfPeople)
	for p := 0; uint(p) < NumberOfPeople; p++ {
		mrSet[p] = make([]MasterRecord, len(Inputs.Chains), len(Inputs.Chains))
		for ch := 0; ch < len(Inputs.Chains); ch++ {

			// current cycle
			var masterRecord MasterRecord
			masterRecord.Person_id = uint(p)
			masterRecord.Chain_id = uint(ch)
			masterRecord.Has_entered_simulation = false
			mrSet[p][ch] = masterRecord

		}
	}

	return mrSet
}

func initializeMasterRecords() {
	// ####################### Master Records & Accessor

	// length := len(Inputs.Chains) * len(Inputs.People)
	// Inputs.CurrentCycle = make([]MasterRecord, length, length)

	Query.Master_record_current_cycle_by_person_and_chain = make([][]MasterRecord, NumberOfPeople, NumberOfPeople)
	for p := 0; uint(p) < NumberOfPeople; p++ {
		Query.Master_record_current_cycle_by_person_and_chain[p] = make([]MasterRecord, len(Inputs.Chains), len(Inputs.Chains))
		for ch := 0; ch < len(Inputs.Chains); ch++ {

			// current cycle
			var masterRecord MasterRecord
			masterRecord.Person_id = uint(p)
			masterRecord.Chain_id = uint(ch)
			masterRecord.Has_entered_simulation = false
			Query.Master_record_current_cycle_by_person_and_chain[p][ch] = masterRecord

		}
	}

	// length := NumberOfPeople * (len(Inputs.Cycles) + 1) * len(Inputs.Chains)
	// fmt.Println("making slice with len ", length)
	// Inputs.MasterRecords = make([]MasterRecord, length, length)

	// i := 0
	// Query.Master_record_id_by_cycle_and_person_and_chain = make([][][]uint, len(Inputs.Cycles)+1, len(Inputs.Cycles)+1)
	// for c, _ := range Query.Master_record_id_by_cycle_and_person_and_chain {
	// 	//People
	// 	Query.Master_record_id_by_cycle_and_person_and_chain[c] = make([][]uint, NumberOfPeople, NumberOfPeople)
	// 	for p, _ := range Query.Master_record_id_by_cycle_and_person_and_chain[c] {
	// 		Query.Master_record_id_by_cycle_and_person_and_chain[c][p] = make([]uint, len(Inputs.Chains), len(Inputs.Chains))
	// 		for m, _ := range Query.Master_record_id_by_cycle_and_person_and_chain[c][p] {
	// 			var masterRecord MasterRecord
	// 			masterRecord.Cycle_id = c
	// 			masterRecord.Person_id = p
	// 			masterRecord.Chain_id = m
	// 			masterRecord.Has_entered_simulation = false
	// 			Inputs.MasterRecords[i] = masterRecord
	// 			Query.Master_record_id_by_cycle_and_person_and_chain[c][p][m] = i
	// 			i++
	// 		}
	// 	}
	// }

}

///////######################## CORE FUNCTIONALITY ###############################
/////////#########################################################################

func calcTransmissionRisks(cycle Cycle) {
	for i := 0; i < len(Inputs.People); i++ {

		//check people's ids line up
		thisPerson := Inputs.People[i]
		if uint(i) != thisPerson.Id {
			fmt.Println("Person Id doesn't make position in array")
			os.Exit(1)
		}

		// if uninfected
		unif_TB_state_id := Query.getStateByName("Uninfected TB").Id
		// active_TB_state_id := Query.getStateByName("Active - untreated").Id
		// active_treat_1_state_id := Query.getStateByName("Active Treated Month 1").Id
		// active_treat_2_state_id := Query.getStateByName("Active Treated Month 2").Id
		tb_chain := Query.getChainByName("TB disease and treatment")

		this_person_state_id := thisPerson.get_state_by_chain(tb_chain, cycle).Id

		isUsb := 0
		if thisPerson.get_state_by_chain(Inputs.Chains[BIRTHPLACE_CHAIN_ID], cycle).Name == "United States" {
			isUsb = 1
		}

		race_state_id := thisPerson.get_state_by_chain(Inputs.Chains[RACE_CHAIN_ID], cycle).Id

		if this_person_state_id == unif_TB_state_id {
			Query.Num_susceptible_by_cycle_isUsb_and_race[cycle.Id][isUsb][race_state_id] += 1
			Query.Total_susceptible_by_cycle[cycle.Id] += 1
		}

		// originally, all people in active + active treat m 1 + active treat m 2 were here
		// but it's 6 per CASE, not 6 per person. this is a more accurate way, since (almost) everyone
		// will eventually be treated, and this is only one month of contributing risk
		// if this_person_state_id == active_treat_1_state_id { //this_person_state_id == active_TB_state_id ||  || this_person_state_id == active_treat_2_state_id {
		Query.Total_active_by_cycle[cycle.Id] += thisPerson.RiskOfProgression

		Query.Num_active_cases_by_cycle_isUsb_and_race[cycle.Id][isUsb][race_state_id] += thisPerson.RiskOfProgression

		// }

	}

	//// -------------------------- NOTE I'VE TAKE OUT TRANSMISSION BY RACE AND BIRTHPLACE FOR NOW

	generalPopulationRisk := float64(Query.Total_active_by_cycle[cycle.Id]) / float64(Query.Total_susceptible_by_cycle[cycle.Id]) * 0.2

	// fmt.Println("In cycle ", cycle.Id, " we have general population risk of: ", generalPopulationRisk)

	// calculate risk
	for isUsb := 0; isUsb < 2; isUsb++ {
		for r := 0; r < len(Inputs.States); r++ {
			numSus := Query.Num_susceptible_by_cycle_isUsb_and_race[cycle.Id][isUsb][r]
			if numSus > 0 {
				numActive := Query.Num_active_cases_by_cycle_isUsb_and_race[cycle.Id][isUsb][r]
				// todo make real

				//xyx

				trans_adjustment := 0.0
				if cycle.Id <= 12 {
					trans_adjustment = 1 //2.1
				} else if cycle.Id > 12 && cycle.Id <= 24 {
					trans_adjustment = 1 //1.1
				} else if cycle.Id > 24 && cycle.Id <= 36 {
					trans_adjustment = 1 //1.1
				} else {
					trans_adjustment = 1.0
				}

				risk := ((float64(numActive)/float64(numSus))*0.8 + generalPopulationRisk) * trans_adjustment * NumberOfLtbiCasesCausedByOneActiveCase.Value

				// if float64(numActive)/float64(numSus) > 0 {
				// 	fmt.Println("risk in ", Inputs.States[b].Name, Inputs.States[r].Name, " is ", float64(numActive)/float64(numSus))
				// }

				if risk > 1 {
					risk = 1
				}
				Query.LTBI_risk_by_cycle_isUsb_and_race[cycle.Id][isUsb][r] = risk
				// fmt.Println("usb ", isUsb, " race ", Inputs.States[r].Name, " risk is ", numActive, " / ", numSus, " = ", risk)

			}
		}
	}

}

func runSimulation(concurrencyBy string, interventionName string, randId uint) {

	var mutex = &sync.Mutex{}

	// msg := "Running " + interventionName + " simulation..."
	// fmt.Println("")
	// fmt.Println(msg)
	// fmt.Println("")

	BeginTime = time.Now()

	generalChan := make(chan uint)

	for _, cycle := range Inputs.Cycles { // foreach cycle

		if cycle.Id > 192 {
			TbTestMonthCutoff = 13
		} else {
			TbTestMonthCutoff = 13
		}

		fmt.Println(cycle.Year, "|", cycle.Id, "|", InterventionId, "|", interventionName, "|", IterationNum, "|", PsaRunNum, "|", time.Now().Format("2006-01-02 15:04"))

		/// Calculate adjustment factors for the interventions based on the population size, regardless of testing

		genpop_untested := 0
		genpop_tested := 0
		fb_untested := 0
		fb_tested := 0
		mrf_untested := 0
		mrf_tested := 0
		hcw_tested := 0
		hcw_untested := 0

		genpop_ever_untested := 0
		genpop_ever_tested := 0
		fb_ever_untested := 0
		fb_ever_tested := 0
		mrf_ever_untested := 0
		mrf_ever_tested := 0

		for _, person := range Inputs.People {

			natrualDeathStateId := Query.Master_record_current_cycle_by_person_and_chain[person.Id][DEATH_CHAIN_ID].State_id
			IsDead := Inputs.States[natrualDeathStateId].Is_death_state

			if !IsDead {

				// ever tested
				if person.LastTbTest != 0 {

					// if InterventionId == 1 {
					// 	fmt.Println(person.LastTbTest)
					// }

					genpop_ever_tested++
					mrfStateId := Query.Master_record_current_cycle_by_person_and_chain[person.Id][MRF_CHAIN_ID].State_id
					mrfStateName := Inputs.States[mrfStateId].Name
					if mrfStateName == "Medical risk factor" {
						mrf_ever_tested++
					}
					birthplaceStateId := Query.Master_record_current_cycle_by_person_and_chain[person.Id][BIRTHPLACE_CHAIN_ID].State_id
					isUsBorn := (birthplaceStateId == US_BIRTHPLACE_ID)
					if !isUsBorn {
						fb_ever_tested++
					}
				} else {
					genpop_ever_untested++
					mrfStateId := Query.Master_record_current_cycle_by_person_and_chain[person.Id][MRF_CHAIN_ID].State_id
					mrfStateName := Inputs.States[mrfStateId].Name
					if mrfStateName == "Medical risk factor" {
						mrf_ever_untested++
					}
					birthplaceStateId := Query.Master_record_current_cycle_by_person_and_chain[person.Id][BIRTHPLACE_CHAIN_ID].State_id
					isUsBorn := (birthplaceStateId == US_BIRTHPLACE_ID)
					if !isUsBorn {
						fb_ever_untested++
					}
				}

				// tested within TbCutoff
				if (person.LastTbTest+TbTestMonthCutoff) >= cycle.Id && person.LastTbTest != 0 {

					// if InterventionId == 1 {
					// 	fmt.Println(person.LastTbTest)
					// }

					genpop_tested++
					mrfStateId := Query.Master_record_current_cycle_by_person_and_chain[person.Id][MRF_CHAIN_ID].State_id
					mrfStateName := Inputs.States[mrfStateId].Name
					if mrfStateName == "Medical risk factor" {
						mrf_tested++
					}
					birthplaceStateId := Query.Master_record_current_cycle_by_person_and_chain[person.Id][BIRTHPLACE_CHAIN_ID].State_id
					isUsBorn := (birthplaceStateId == US_BIRTHPLACE_ID)
					if !isUsBorn {
						fb_tested++
					}
					if person.IsHcw {
						hcw_tested++
					}

				} else {
					genpop_untested++
					mrfStateId := Query.Master_record_current_cycle_by_person_and_chain[person.Id][MRF_CHAIN_ID].State_id
					mrfStateName := Inputs.States[mrfStateId].Name
					if mrfStateName == "Medical risk factor" {
						mrf_untested++
					}
					birthplaceStateId := Query.Master_record_current_cycle_by_person_and_chain[person.Id][BIRTHPLACE_CHAIN_ID].State_id
					isUsBorn := (birthplaceStateId == US_BIRTHPLACE_ID)
					if !isUsBorn {
						fb_untested++
					}
					if person.IsHcw {
						hcw_untested++
					}
				}
			}

		}

		if cycle.Id > 12 {

			// within Tb testing timeframe
			genpop_adjustment := (float64(genpop_untested) + float64(genpop_tested)) / float64(genpop_untested)
			fb_adjustment := (float64(fb_untested) + float64(fb_tested)) / float64(fb_untested)
			mrf_adjustment := (float64(mrf_untested) + float64(mrf_tested)) / float64(mrf_untested)

			//ever tested vs never tested (called here "ever_untested" for ease of copy+paste)
			genpop_ever_adjustment := (float64(genpop_ever_untested) + float64(genpop_ever_tested)) / float64(genpop_ever_untested)
			fb_ever_adjustment := (float64(fb_ever_untested) + float64(fb_ever_tested)) / float64(fb_ever_untested)
			mrf_ever_adjustment := (float64(mrf_ever_untested) + float64(mrf_ever_tested)) / float64(mrf_ever_untested)

			// genpop_adjustment = 1
			// fb_adjustment = 1
			// mrf_adjustment = 1

			// fmt.Println("genpop_adjustment", genpop_adjustment)
			// fmt.Println("fb_adjustment", fb_adjustment)
			// fmt.Println("mrf_adjustment", mrf_adjustment)

			// fmt.Println("genpop_ever_adjustment", genpop_ever_adjustment)
			// fmt.Println("fb_ever_adjustment", fb_ever_adjustment)
			// fmt.Println("mrf_ever_adjustment", mrf_ever_adjustment)

			genpop_intervention_adjustment := 0.0
			fb_intervention_adjustment := 0.0
			mrf_intervention_adjustment := 0.0

			if Disallow_retest == 1 {
				genpop_intervention_adjustment = genpop_ever_adjustment
				fb_intervention_adjustment = fb_ever_adjustment
				mrf_intervention_adjustment = mrf_ever_adjustment
			} else {
				genpop_intervention_adjustment = genpop_adjustment
				fb_intervention_adjustment = fb_adjustment
				mrf_intervention_adjustment = mrf_adjustment
			}

			// --------------------- Full pop ---------------------------

			base_rate_w_hcw := 0.000833333*2.0 + 0.003879032 // .003879032 = monthly HCW testing

			if SimName == "basecase" {

				// basecase
				Inputs.Interventions[0].Testing_groups[0].Monthly_testing_uptake = 0.000833333 * genpop_adjustment
				Inputs.Interventions[0].Testing_groups[1].Monthly_testing_uptake = 0.000833333 * genpop_adjustment

			}

			if SimName == "full-pop" {

				// basecase
				Inputs.Interventions[0].Testing_groups[0].Monthly_testing_uptake = 0.000833333 * genpop_adjustment
				Inputs.Interventions[0].Testing_groups[1].Monthly_testing_uptake = 0.000833333 * genpop_adjustment
				// 2x
				Inputs.Interventions[1].Testing_groups[0].Monthly_testing_uptake = 0.000833333 * genpop_adjustment
				Inputs.Interventions[1].Testing_groups[1].Monthly_testing_uptake = 0.000833333 * genpop_adjustment
				Inputs.Interventions[1].Testing_groups[2].Monthly_testing_uptake = base_rate_w_hcw * genpop_intervention_adjustment
				// 4x
				Inputs.Interventions[2].Testing_groups[0].Monthly_testing_uptake = 0.000833333 * genpop_adjustment
				Inputs.Interventions[2].Testing_groups[1].Monthly_testing_uptake = 0.000833333 * genpop_adjustment
				Inputs.Interventions[2].Testing_groups[2].Monthly_testing_uptake = base_rate_w_hcw * 3.0 * genpop_intervention_adjustment
				// 10x
				Inputs.Interventions[3].Testing_groups[0].Monthly_testing_uptake = 0.000833333 * genpop_adjustment
				Inputs.Interventions[3].Testing_groups[1].Monthly_testing_uptake = 0.000833333 * genpop_adjustment
				Inputs.Interventions[3].Testing_groups[2].Monthly_testing_uptake = base_rate_w_hcw * 9.0 * genpop_intervention_adjustment

			}

			// --------------------- FB ---------------------------

			if SimName == "fb" {

				// basecase
				Inputs.Interventions[0].Testing_groups[0].Monthly_testing_uptake = 0.000833333 * genpop_adjustment // 0.000833333 = 2% annual testing in non-HCW
				Inputs.Interventions[0].Testing_groups[1].Monthly_testing_uptake = 0.000833333 * genpop_adjustment
				// 2x
				Inputs.Interventions[1].Testing_groups[0].Monthly_testing_uptake = 0.000833333 * genpop_adjustment
				Inputs.Interventions[1].Testing_groups[1].Monthly_testing_uptake = 0.000833333 * genpop_adjustment
				Inputs.Interventions[1].Testing_groups[2].Monthly_testing_uptake = base_rate_w_hcw * fb_intervention_adjustment //* 2.0 //va

				// 4x
				Inputs.Interventions[2].Testing_groups[0].Monthly_testing_uptake = 0.000833333 * genpop_adjustment
				Inputs.Interventions[2].Testing_groups[1].Monthly_testing_uptake = 0.000833333 * genpop_adjustment
				Inputs.Interventions[2].Testing_groups[2].Monthly_testing_uptake = base_rate_w_hcw * 3.0 * fb_intervention_adjustment //* 1.333 //v

				// 10x
				Inputs.Interventions[3].Testing_groups[0].Monthly_testing_uptake = 0.000833333 * genpop_adjustment
				Inputs.Interventions[3].Testing_groups[1].Monthly_testing_uptake = 0.000833333 * genpop_adjustment
				Inputs.Interventions[3].Testing_groups[2].Monthly_testing_uptake = base_rate_w_hcw * 9.0 * fb_intervention_adjustment //* 1.111 //v

			}

			// !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! DID NOT ADJUST BELOW !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

			// --------------------- MRF ---------------------------

			if SimName == "med-risk-factor" {

				// basecase
				Inputs.Interventions[0].Testing_groups[0].Monthly_testing_uptake = 0.000833333 * genpop_adjustment
				Inputs.Interventions[0].Testing_groups[1].Monthly_testing_uptake = 0.000833333 * genpop_adjustment
				// 2x
				Inputs.Interventions[1].Testing_groups[0].Monthly_testing_uptake = 0.000833333 * genpop_adjustment
				Inputs.Interventions[1].Testing_groups[1].Monthly_testing_uptake = 0.000833333 * genpop_adjustment
				Inputs.Interventions[1].Testing_groups[2].Monthly_testing_uptake = base_rate_w_hcw * mrf_intervention_adjustment
				// 4x
				Inputs.Interventions[2].Testing_groups[0].Monthly_testing_uptake = 0.000833333 * genpop_adjustment
				Inputs.Interventions[2].Testing_groups[1].Monthly_testing_uptake = 0.000833333 * genpop_adjustment
				Inputs.Interventions[2].Testing_groups[2].Monthly_testing_uptake = base_rate_w_hcw * 3.0 * mrf_intervention_adjustment
				// 10x
				Inputs.Interventions[3].Testing_groups[0].Monthly_testing_uptake = 0.000833333 * genpop_adjustment
				Inputs.Interventions[3].Testing_groups[1].Monthly_testing_uptake = 0.000833333 * genpop_adjustment
				Inputs.Interventions[3].Testing_groups[2].Monthly_testing_uptake = base_rate_w_hcw * 9.0 * mrf_intervention_adjustment

			}

			// --------------------- FB + MRF ---------------------------

			if SimName == "fb-and-med-risk-factor" {

				// basecase
				Inputs.Interventions[0].Testing_groups[0].Monthly_testing_uptake = 0.000833333 * genpop_adjustment
				Inputs.Interventions[0].Testing_groups[1].Monthly_testing_uptake = 0.000833333 * genpop_adjustment
				// 2x
				Inputs.Interventions[1].Testing_groups[0].Monthly_testing_uptake = 0.000833333 * genpop_adjustment
				Inputs.Interventions[1].Testing_groups[1].Monthly_testing_uptake = 0.000833333 * genpop_adjustment
				Inputs.Interventions[1].Testing_groups[2].Monthly_testing_uptake = base_rate_w_hcw * fb_intervention_adjustment
				Inputs.Interventions[1].Testing_groups[3].Monthly_testing_uptake = base_rate_w_hcw * mrf_intervention_adjustment
				// 4x
				Inputs.Interventions[2].Testing_groups[0].Monthly_testing_uptake = 0.000833333 * genpop_adjustment
				Inputs.Interventions[2].Testing_groups[1].Monthly_testing_uptake = 0.000833333 * genpop_adjustment
				Inputs.Interventions[2].Testing_groups[2].Monthly_testing_uptake = base_rate_w_hcw * 3.0 * fb_intervention_adjustment
				Inputs.Interventions[2].Testing_groups[3].Monthly_testing_uptake = base_rate_w_hcw * 3.0 * mrf_intervention_adjustment
				// 10x
				Inputs.Interventions[3].Testing_groups[0].Monthly_testing_uptake = 0.000833333 * genpop_adjustment
				Inputs.Interventions[3].Testing_groups[1].Monthly_testing_uptake = 0.000833333 * genpop_adjustment
				Inputs.Interventions[3].Testing_groups[2].Monthly_testing_uptake = base_rate_w_hcw * 9.0 * fb_intervention_adjustment
				Inputs.Interventions[3].Testing_groups[3].Monthly_testing_uptake = base_rate_w_hcw * 9.0 * mrf_intervention_adjustment

			}

			if SimName != "basecase" && SimName != "full-pop" && SimName != "fb" && SimName != "med-risk-factor" && SimName != "fb-and-med-risk-factor" {
				fmt.Println("invalid sim name")
				os.Exit(1)
			}
		} else {

			// less than cycle 12

			// --------------------- Full pop ---------------------------

			if SimName == "basecase" {

				// basecase
				Inputs.Interventions[0].Testing_groups[0].Monthly_testing_uptake = 0.000833333
				Inputs.Interventions[0].Testing_groups[1].Monthly_testing_uptake = 0.000833333

			}

			if SimName == "full-pop" {

				// basecase
				Inputs.Interventions[0].Testing_groups[0].Monthly_testing_uptake = 0.000833333
				Inputs.Interventions[0].Testing_groups[1].Monthly_testing_uptake = 0.000833333
				// 2x
				Inputs.Interventions[1].Testing_groups[0].Monthly_testing_uptake = 0.000833333
				Inputs.Interventions[1].Testing_groups[1].Monthly_testing_uptake = 0.000833333
				Inputs.Interventions[1].Testing_groups[2].Monthly_testing_uptake = 0.000833333
				// 4x
				Inputs.Interventions[2].Testing_groups[0].Monthly_testing_uptake = 0.000833333
				Inputs.Interventions[2].Testing_groups[1].Monthly_testing_uptake = 0.000833333
				Inputs.Interventions[2].Testing_groups[2].Monthly_testing_uptake = 0.000833333
				// 10x
				Inputs.Interventions[3].Testing_groups[0].Monthly_testing_uptake = 0.000833333
				Inputs.Interventions[3].Testing_groups[1].Monthly_testing_uptake = 0.000833333
				Inputs.Interventions[3].Testing_groups[2].Monthly_testing_uptake = 0.000833333

			}

			// --------------------- FB ---------------------------

			if SimName == "fb" {

				// basecase
				Inputs.Interventions[0].Testing_groups[0].Monthly_testing_uptake = 0.000833333
				Inputs.Interventions[0].Testing_groups[1].Monthly_testing_uptake = 0.000833333
				// 2x
				Inputs.Interventions[1].Testing_groups[0].Monthly_testing_uptake = 0.000833333
				Inputs.Interventions[1].Testing_groups[1].Monthly_testing_uptake = 0.000833333
				Inputs.Interventions[1].Testing_groups[2].Monthly_testing_uptake = 0.000833333
				// 4x
				Inputs.Interventions[2].Testing_groups[0].Monthly_testing_uptake = 0.000833333
				Inputs.Interventions[2].Testing_groups[1].Monthly_testing_uptake = 0.000833333
				Inputs.Interventions[2].Testing_groups[2].Monthly_testing_uptake = 0.000833333
				// 10x
				Inputs.Interventions[3].Testing_groups[0].Monthly_testing_uptake = 0.000833333
				Inputs.Interventions[3].Testing_groups[1].Monthly_testing_uptake = 0.000833333
				Inputs.Interventions[3].Testing_groups[2].Monthly_testing_uptake = 0.000833333

			}

			// --------------------- MRF ---------------------------

			if SimName == "med-risk-factor" {

				// basecase
				Inputs.Interventions[0].Testing_groups[0].Monthly_testing_uptake = 0.000833333
				Inputs.Interventions[0].Testing_groups[1].Monthly_testing_uptake = 0.000833333
				// 2x
				Inputs.Interventions[1].Testing_groups[0].Monthly_testing_uptake = 0.000833333
				Inputs.Interventions[1].Testing_groups[1].Monthly_testing_uptake = 0.000833333
				Inputs.Interventions[1].Testing_groups[2].Monthly_testing_uptake = 0.000833333
				// 4x
				Inputs.Interventions[2].Testing_groups[0].Monthly_testing_uptake = 0.000833333
				Inputs.Interventions[2].Testing_groups[1].Monthly_testing_uptake = 0.000833333
				Inputs.Interventions[2].Testing_groups[2].Monthly_testing_uptake = 0.000833333
				// 10x
				Inputs.Interventions[3].Testing_groups[0].Monthly_testing_uptake = 0.000833333
				Inputs.Interventions[3].Testing_groups[1].Monthly_testing_uptake = 0.000833333
				Inputs.Interventions[3].Testing_groups[2].Monthly_testing_uptake = 0.000833333

			}

			// --------------------- FB + MRF ---------------------------

			if SimName == "fb-and-med-risk-factor" {

				// basecase
				Inputs.Interventions[0].Testing_groups[0].Monthly_testing_uptake = 0.000833333
				Inputs.Interventions[0].Testing_groups[1].Monthly_testing_uptake = 0.000833333
				// 2x
				Inputs.Interventions[1].Testing_groups[0].Monthly_testing_uptake = 0.000833333
				Inputs.Interventions[1].Testing_groups[1].Monthly_testing_uptake = 0.000833333
				Inputs.Interventions[1].Testing_groups[2].Monthly_testing_uptake = 0.000833333
				Inputs.Interventions[1].Testing_groups[3].Monthly_testing_uptake = 0.000833333
				// 4x
				Inputs.Interventions[2].Testing_groups[0].Monthly_testing_uptake = 0.000833333
				Inputs.Interventions[2].Testing_groups[1].Monthly_testing_uptake = 0.000833333
				Inputs.Interventions[2].Testing_groups[2].Monthly_testing_uptake = 0.000833333
				Inputs.Interventions[2].Testing_groups[3].Monthly_testing_uptake = 0.000833333
				// 10x
				Inputs.Interventions[3].Testing_groups[0].Monthly_testing_uptake = 0.000833333
				Inputs.Interventions[3].Testing_groups[1].Monthly_testing_uptake = 0.000833333
				Inputs.Interventions[3].Testing_groups[2].Monthly_testing_uptake = 0.000833333
				Inputs.Interventions[3].Testing_groups[3].Monthly_testing_uptake = 0.000833333

			}

		}

		// fmt.Println("=== Gen Pop ===")
		// fmt.Println("Untested within year: ", genpop_untested)
		// fmt.Println("Tested within year: ", genpop_tested)
		// fmt.Println("Never tested: ", genpop_ever_untested)
		// fmt.Println("Ever tested: ", genpop_ever_tested)
		// if genpop_untested != 0 {
		// 	fmt.Println("% Tested within year: ", float32(genpop_tested)/float32(genpop_tested+genpop_untested))
		// }
		// if genpop_untested != 0 {
		// 	fmt.Println("% Ever Tested: ", float32(genpop_ever_tested)/float32(genpop_ever_tested+genpop_ever_untested))
		// }

		// fmt.Println("=== FB ===")
		// fmt.Println("Untested within year: ", fb_untested)
		// fmt.Println("Tested within year: ", fb_tested)
		// if fb_untested != 0 {
		// 	fmt.Println("% Tested within year: ", float32(fb_tested)/float32(fb_tested+fb_untested))
		// }
		// if fb_untested != 0 {
		// 	fmt.Println("% Ever Tested: ", float32(fb_ever_tested)/float32(fb_ever_tested+fb_ever_untested))
		// }

		// fmt.Println("=== MRF ===")
		// fmt.Println("Untested within year: ", mrf_untested)
		// fmt.Println("Tested  within year: ", mrf_tested)
		// if mrf_untested != 0 {
		// 	fmt.Println("% Tested within year: ", float32(mrf_tested)/float32(mrf_tested+mrf_untested))
		// }
		// if mrf_untested != 0 {
		// 	fmt.Println("% Ever Tested: ", float32(mrf_ever_tested)/float32(mrf_ever_tested+mrf_ever_untested))
		// }

		// fmt.Println("=== HCW ===")
		// fmt.Println("HCW tested within year: ", hcw_tested)
		// fmt.Println("HCW untested within year: ", hcw_untested)
		// if hcw_tested != 0 {
		// 	fmt.Println("% Tested within year: ", float32(hcw_tested)/float32(hcw_tested+hcw_untested))
		// }

		RandomController.initialize(cycle.Id)

		// "next cycle" is now "this cycle". unless cycle == 0, in which case just use a blank. copy(dest, source)
		if cycle.Id == 0 {
			Query.Master_record_next_cycle_by_person_and_chain = blankMasterRecordsSet()
		} else {
			Query.Master_record_current_cycle_by_person_and_chain = Query.Master_record_next_cycle_by_person_and_chain
			Query.Master_record_next_cycle_by_person_and_chain = blankMasterRecordsSet()
		}

		//printMemoryUse("Top of cycle " + strconv.Itoa(int(cycle.Id)))

		Query.Total_population_by_cycle[cycle.Id] = uint(len(Inputs.People))

		//printMemoryUse("After age adjustments, cycle " + strconv.Itoa(int(cycle.Id)))

		// fmt.Println("Cycle: ", cycle.Name, " People: ", len(Inputs.People))

		/// phase one : initialize population, store results in cycle 0
		if cycle.Id == 0 { // initialize

			for _, person := range Inputs.People { // 	foreach person
				go initializeOnePerson(cycle, person, generalChan, mutex)
			}

			for _, person := range Inputs.People { // 	foreach person
				chanString := <-generalChan
				_ = person     // to avoid unused warning
				_ = cycle      // to avoid unused warning
				_ = chanString // to avoid unused warning
			}

		}

		//printMemoryUse("After initializing people into models, cycle " + strconv.Itoa(int(cycle.Id)))

		// need to create new people before calculating the year
		// of they're uninit states will be written over
		if cycle.Id > 0 {
			if IsClosedCohort != 1 {
				createNewPeople(cycle, NumberOfPeopleEnteringPerYear, mutex) //=The number of created people per cycle
			}
		}

		calcTransmissionRisks(cycle)

		//printMemoryUse("After initializing people into models, cycle" + strconv.Itoa(int(cycle.Id)))

		for _, person := range Inputs.People { // 	foreach person
			go runOneCycleForOnePerson(cycle.Id, person.Id, generalChan)

		}

		for _, person := range Inputs.People { // 	foreach person
			chanString := <-generalChan
			_ = person     // to avoid unused warning
			_ = cycle      // to avoid unused warning
			_ = chanString // to avoid unused warning
		}

		//printMemoryUse("After running cycle for one person, cycle" + strconv.Itoa(int(cycle.Id)))

		addThisCycleToOutputs(cycle.Id) // this saves cycle 0

		// TODO what is this for?
		randId = randId + NumberOfPeople*uint(len(Inputs.Cycles))

	}

	fmt.Println("")
	fmt.Println("Time elapsed, excluding data import and export:", fmt.Sprint(time.Since(BeginTime)))

	for i := 0; i < len(Outputs.OutputsByCycleStateFull); i++ {
		Outputs.OutputsByCycleStateFull[i].Iteration_num = IterationNum
		Outputs.OutputsByCycleStateFull[i].Intervention_id = InterventionId
		Outputs.OutputsByCycleStateFull[i].Psa_iteration_num = PsaRunNum
	}

}

func makeOutputs() {

	fmt.Println("tested through active case finding: ", TestedThroughActiveCaseFinding)

	// if RunType == "single" {

	fmt.Println("Beginning export...")

	// if RunType == "calib" {

	// 	head := SimName + "_" + strconv.Itoa(int(TheSeed)) + "_calib.csv"
	// 	filename := "/cycle_state/" + head

	// 	toCsv(Output_dir+filename, GlobalOutputs.OutputsByCycleStateFull[0], GlobalOutputs.OutputsByCycleStateFull)

	// }

	if RunType == "psa" || RunType == "calib" {

		fmt.Println("Beginning export...")

		head := SimName + "_" + strconv.Itoa(int(TheSeed)) + ".csv"

		filename := RunName + "/" + SimName + "/" + head

		limitedOutputs := []OutputByCycleStateLimited{}
		for i := 0; i < len(GlobalOutputs.OutputsByCycleStateFull); i++ {

			sn := GlobalOutputs.OutputsByCycleStateFull[i].State_name

			if sn == "No medical risk factor" ||
				sn == "Medical risk factor" ||
				sn == "Infected HIV, no ART" ||
				sn == "Infected HIV, ART" ||
				sn == "Diabetes" ||
				sn == "ESRD" ||
				sn == "Smoker" ||
				sn == "Transplant patient" ||
				sn == "TNF-alpha" ||
				sn == "Life" ||
				sn == "Black" ||
				sn == "Asian" ||
				sn == "Hispanic" ||
				sn == "White" ||
				sn == "Other" ||
				sn == "Uninfected TB" ||
				sn == "Slow latent" ||
				sn == "Fast latent" ||
				sn == "Less than one year" ||
				sn == "LTBI treated with RTP" ||
				sn == "LBTI 9m INH - Month 1" ||
				sn == "LBTI 9m INH - Month 2" ||
				sn == "LBTI 9m INH - Month 3" ||
				sn == "LBTI 9m INH - Month 4" ||
				sn == "LBTI 9m INH - Month 5" ||
				sn == "LBTI 9m INH - Month 6" ||
				sn == "LBTI 9m INH - Month 7" ||
				sn == "LBTI 9m INH - Month 8" ||
				sn == "LBTI 9m INH - Month 9" ||
				sn == "LTBI 6m INH - Month 1" ||
				sn == "LTBI 6m INH - Month 2" ||
				sn == "LTBI 6m INH - Month 3" ||
				sn == "LTBI 6m INH - Month 4" ||
				sn == "LTBI 6m INH - Month 5" ||
				sn == "LTBI 6m INH - Month 6" ||
				sn == "LTBI RIF - Month 1" ||
				sn == "LTBI RIF - Month 2" ||
				sn == "LTBI RIF - Month 3" ||
				sn == "LTBI RIF - Month 4" ||
				sn == "LTBI RTP - Month 1" ||
				sn == "LTBI RTP - Month 2" ||
				sn == "LTBI RTP - Month 3" ||
				sn == "FP LBTI 9m INH - Month 1" ||
				sn == "FP LBTI 9m INH - Month 2" ||
				sn == "FP LBTI 9m INH - Month 3" ||
				sn == "FP LBTI 9m INH - Month 4" ||
				sn == "FP LBTI 9m INH - Month 5" ||
				sn == "FP LBTI 9m INH - Month 6" ||
				sn == "FP LBTI 9m INH - Month 7" ||
				sn == "FP LBTI 9m INH - Month 8" ||
				sn == "FP LBTI 9m INH - Month 9" ||
				sn == "FP LTBI 6m INH - Month 1" ||
				sn == "FP LTBI 6m INH - Month 2" ||
				sn == "FP LTBI 6m INH - Month 3" ||
				sn == "FP LTBI 6m INH - Month 4" ||
				sn == "FP LTBI 6m INH - Month 5" ||
				sn == "FP LTBI 6m INH - Month 6" ||
				sn == "FP LTBI RIF - Month 1" ||
				sn == "FP LTBI RIF - Month 2" ||
				sn == "FP LTBI RIF - Month 3" ||
				sn == "FP LTBI RIF - Month 4" ||
				sn == "FP LTBI RTP - Month 1" ||
				sn == "FP LTBI RTP - Month 2" ||
				sn == "FP LTBI RTP - Month 3" ||
				sn == "Active Treated Month 1" ||
				sn == "Active Treated Month 2" ||
				sn == "Active Treated Month 3" ||
				sn == "Active Treated Month 4" ||
				sn == "Active Treated Month 5" ||
				sn == "Active Treated Month 6" ||
				sn == "Infected Testing TST" ||
				sn == "Infected Testing QFT" ||
				sn == "Infected Testing TSPOT" ||
				sn == "Infected Testing TST+QFT" ||
				sn == "Infected Testing TST+TSPOT" ||
				sn == "Uninfected Testing TST" ||
				sn == "Uninfected Testing QFT" ||
				sn == "Uninfected Testing TSPOT" ||
				sn == "Uninfected Testing TST+QFT" ||
				sn == "Uninfected Testing TST+TSPOT" {

				if GlobalOutputs.OutputsByCycleStateFull[i].Year > 1999 { // 2015 remove if you want to look at calibration

					var limitedOutput OutputByCycleStateLimited
					limitedOutput.Iteration_num = GlobalOutputs.OutputsByCycleStateFull[i].Iteration_num
					limitedOutput.Population = GlobalOutputs.OutputsByCycleStateFull[i].Population
					limitedOutput.Population_us = GlobalOutputs.OutputsByCycleStateFull[i].Population_us
					limitedOutput.Population_fb = GlobalOutputs.OutputsByCycleStateFull[i].Population_fb
					limitedOutput.Costs = GlobalOutputs.OutputsByCycleStateFull[i].Costs
					limitedOutput.Cycle_id = GlobalOutputs.OutputsByCycleStateFull[i].Cycle_id
					limitedOutput.State_id = GlobalOutputs.OutputsByCycleStateFull[i].State_id
					limitedOutput.Intervention_id = GlobalOutputs.OutputsByCycleStateFull[i].Intervention_id
					limitedOutput.Intervention_name = GlobalOutputs.OutputsByCycleStateFull[i].Intervention_name
					limitedOutput.Risk_of_prog_us = GlobalOutputs.OutputsByCycleStateFull[i].Risk_of_prog_us
					limitedOutput.Risk_of_prog_fb = GlobalOutputs.OutputsByCycleStateFull[i].Risk_of_prog_fb
					limitedOutput.Months_life_remaining_us = GlobalOutputs.OutputsByCycleStateFull[i].Months_life_remaining_us
					limitedOutput.Months_life_remaining_fb = GlobalOutputs.OutputsByCycleStateFull[i].Months_life_remaining_fb
					limitedOutput.Psa_iteration_num = GlobalOutputs.OutputsByCycleStateFull[i].Psa_iteration_num
					limitedOutput.State_name = GlobalOutputs.OutputsByCycleStateFull[i].State_name
					limitedOutput.Age = GlobalOutputs.OutputsByCycleStateFull[i].Age
					limitedOutput.Year = GlobalOutputs.OutputsByCycleStateFull[i].Year
					limitedOutput.HCW_in_state = GlobalOutputs.OutputsByCycleStateFull[i].HCW_in_state

					limitedOutput.Recent_transmission_fb = GlobalOutputs.OutputsByCycleStateFull[i].Recent_transmission_fb
					limitedOutput.Recent_transmission_fb_rop = GlobalOutputs.OutputsByCycleStateFull[i].Recent_transmission_fb_rop
					limitedOutput.Recent_transmission_us = GlobalOutputs.OutputsByCycleStateFull[i].Recent_transmission_us
					limitedOutput.Recent_transmission_us_rop = GlobalOutputs.OutputsByCycleStateFull[i].Recent_transmission_us_rop

					limitedOutputs = append(limitedOutputs, limitedOutput)

				}

			}

		}

		toCsv(Output_dir+filename, limitedOutputs[0], limitedOutputs)

	}

	// 	filename := Output_dir + "/otherPSA/" + SimName + "_output_by_cycle_and_state_psa_interv_" + strconv.Itoa(InterventionId) + ".csv"
	// 	toCsv(filename, Outputs.OutputsByCycleStatePsa[0], Outputs.OutputsByCycleStatePsa)

	// 	filename = Output_dir + "/eventsPSA/" + SimName + "_output_by_cycle_psa_interv_" + strconv.Itoa(InterventionId) + ".csv"
	// 	toCsv(filename, Outputs.OutputsByCycle[0], Outputs.OutputsByCycle)
	// }

	// if RunType == "dsa" {

	// 	filename := Output_dir + "/otherDSA/" + "output_by_cycle_and_state_dsa_interv_" + strconv.Itoa(InterventionId) + "_" + strconv.Itoa(VariableCount) + "_" + strconv.Itoa(WithinVariableCount) + ".csv"
	// 	toCsv(filename, Outputs.OutputsByCycleStatePsa[0], Outputs.OutputsByCycleStatePsa)

	// 	filename = Output_dir + "/eventsDSA/" + "output_by_cycle_dsa_interv_" + strconv.Itoa(InterventionId) + "_" + strconv.Itoa(VariableCount) + "_" + strconv.Itoa(WithinVariableCount) + ".csv"
	// 	toCsv(filename, Outputs.OutputsByCycle[0], Outputs.OutputsByCycle)
	// }

	// fmt.Println("Time elapsed, including data export:", fmt.Sprint(time.Since(BeginTime)))

	// variable := Variable{}
	// db.Find(&variable, "name = ?", "Is simulation done")
	// variable.Value = 1.0
	// db.Save(&variable)

}

func runInterventions(NumberOfIterations uint) {

	concurrencyBy := "person-within-cycle"

	randId := 0

	for i := 0; uint(i) < NumberOfIterations; i++ {

		IterationNum = uint(i)

		// this is used to seed the sampling to ensure samples are
		// identical within iterations
		// needs to be run before people are created, to ensure that the
		// original population samples are identitical
		IterationSeed = rand.Intn(10000)

		fmt.Println("Iteration seed is: ", IterationSeed)

		// if PSA, want as much randomness as possible, so use time
		// may want to change this if we decide to have similar iterations
		// within each PSA run

		for p, eachIntervention := range Inputs.Interventions {

			InterventionId = eachIntervention.Id
			//interventionInitiate(eachIntervention)

			ReducedChains = getReducedChains()

			//set up Query
			Query.setUp()

			//printMemoryUse("After second query set-up ")

			initializeMasterRecords()

			//printMemoryUse("After initialize master records ")

			//build people
			Inputs.People = []Person{}
			Inputs = createInitialPeople(Inputs)

			//printMemoryUse("After create initial people ")

			if p == 0 {
				RandomController.initializeRandomListShuffle()
				// needs to be made after people are created
				// RandomController.initialize()
				// rand.Seed(int64(IterationNum))
			}
			// RandomController.resetCounters()

			//printMemoryUse("After random controller ")

			runSimulation(concurrencyBy, eachIntervention.Name, uint(randId))

			//fmt.Println("count is", count)
			GlobalOutputs.OutputsByCycle = append(GlobalOutputs.OutputsByCycle, Outputs.OutputsByCycle...)

			// fmt.Println("Appending ", len(Outputs.OutputsByCycle), " rows -> ", len(GlobalOutputs.OutputsByCycle))

			GlobalOutputs.OutputsByCycleStateFull = append(GlobalOutputs.OutputsByCycleStateFull, Outputs.OutputsByCycleStateFull...)

			//fmt.Println("Appending ", len(Outputs.OutputsByCycleStateFull), " rows -> ", len(GlobalOutputs.OutputsByCycleStateFull))

			// this is for calibration
			if RunType == "calib" {
				collateResults()
			}

			//clear results from last run
			Inputs.People = []Person{}
			Inputs.MasterRecords = []MasterRecord{}
			Outputs.OutputsByCycle = []OutputByCycle{}
			Outputs.OutputsByCycleStateFull = []OutputByCycleState{}
		}

	}

	// compareToRvct()
	// os.Exit(1)

	// this is for calibration
	// if RunType == "calib" {
	// 	b, err := json.Marshal(Query.OutputYears)
	// 	_ = err
	// 	//fmt.Println(string(b))

	// 	err = ioutil.WriteFile("go/tmp/model_calib_results.json", b, 0644)
	// 	check(err)
	// 	fmt.Println("Printed calibration data.")

	// }

}

// used for calibration
func collateResults() {

	for _, outputCS := range Outputs.OutputsByCycleStateFull {

		// years := []string{"2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026", "2027", "2028", "2029", "2030", "2031", "2032", "2033", "2034", "2035"}

		// groups := []string{"Total", "Homeless", "HIV", "Diabetes",

		if int(Inputs.Cycles[outputCS.Cycle_id].Year) < 2015 {

			year := strconv.Itoa(int(Inputs.Cycles[outputCS.Cycle_id].Year))

			var new_state_name string
			new_state_name = outputCS.State_name

			switch outputCS.State_name {

			case "Life":
				Query.Iteration_year_group[IterationNum][year]["Total"]["USB"] += outputCS.Risk_of_prog_us * RunAdjustment
				Query.Iteration_year_group[IterationNum][year]["Total"]["FB"] += outputCS.Risk_of_prog_fb * RunAdjustment
				new_state_name = "Total"

			case "Homeless":
				Query.Iteration_year_group[IterationNum][year]["Homeless"]["USB"] += outputCS.Risk_of_prog_us * RunAdjustment
				Query.Iteration_year_group[IterationNum][year]["Homeless"]["FB"] += outputCS.Risk_of_prog_fb * RunAdjustment

			case "Infected HIV, no ART":
				Query.Iteration_year_group[IterationNum][year]["HIV"]["USB"] += outputCS.Risk_of_prog_us * RunAdjustment
				Query.Iteration_year_group[IterationNum][year]["HIV"]["FB"] += outputCS.Risk_of_prog_fb * RunAdjustment
				new_state_name = "HIV"

			case "Infected HIV, ART":
				Query.Iteration_year_group[IterationNum][year]["HIV"]["USB"] += outputCS.Risk_of_prog_us * RunAdjustment
				Query.Iteration_year_group[IterationNum][year]["HIV"]["FB"] += outputCS.Risk_of_prog_fb * RunAdjustment
				new_state_name = "HIV"

			case "Diabetes":
				Query.Iteration_year_group[IterationNum][year]["Diabetes"]["USB"] += outputCS.Risk_of_prog_us * RunAdjustment
				Query.Iteration_year_group[IterationNum][year]["Diabetes"]["FB"] += outputCS.Risk_of_prog_fb * RunAdjustment

			//"ESRD"
			case "ESRD":
				Query.Iteration_year_group[IterationNum][year]["ESRD"]["USB"] += outputCS.Risk_of_prog_us * RunAdjustment
				Query.Iteration_year_group[IterationNum][year]["ESRD"]["FB"] += outputCS.Risk_of_prog_fb * RunAdjustment

			// "Smokers"
			case "Smoker":
				Query.Iteration_year_group[IterationNum][year]["Smokers"]["USB"] += outputCS.Risk_of_prog_us * RunAdjustment
				Query.Iteration_year_group[IterationNum][year]["Smokers"]["FB"] += outputCS.Risk_of_prog_fb * RunAdjustment
				new_state_name = "Smokers"

			// "Transplant"
			case "Transplant patient":
				Query.Iteration_year_group[IterationNum][year]["Transplant"]["USB"] += outputCS.Risk_of_prog_us * RunAdjustment
				Query.Iteration_year_group[IterationNum][year]["Transplant"]["FB"] += outputCS.Risk_of_prog_fb * RunAdjustment
				new_state_name = "Transplant"

			// "TNF-alpha"
			case "TNF-alpha":
				Query.Iteration_year_group[IterationNum][year]["TNF-alpha"]["USB"] += outputCS.Risk_of_prog_us * RunAdjustment
				Query.Iteration_year_group[IterationNum][year]["TNF-alpha"]["FB"] += outputCS.Risk_of_prog_fb * RunAdjustment

			// "Asian"
			case "Asian":
				Query.Iteration_year_group[IterationNum][year]["Asian"]["USB"] += outputCS.Risk_of_prog_us * RunAdjustment
				Query.Iteration_year_group[IterationNum][year]["Asian"]["FB"] += outputCS.Risk_of_prog_fb * RunAdjustment

			// "Black"
			case "Black":
				Query.Iteration_year_group[IterationNum][year]["Black"]["USB"] += outputCS.Risk_of_prog_us * RunAdjustment
				Query.Iteration_year_group[IterationNum][year]["Black"]["FB"] += outputCS.Risk_of_prog_fb * RunAdjustment

			// "Hispanic"
			case "Hispanic":
				Query.Iteration_year_group[IterationNum][year]["Hispanic"]["USB"] += outputCS.Risk_of_prog_us * RunAdjustment
				Query.Iteration_year_group[IterationNum][year]["Hispanic"]["FB"] += outputCS.Risk_of_prog_fb * RunAdjustment

			// "Other"
			case "Other":
				Query.Iteration_year_group[IterationNum][year]["Other"]["USB"] += outputCS.Risk_of_prog_us * RunAdjustment
				Query.Iteration_year_group[IterationNum][year]["Other"]["FB"] += outputCS.Risk_of_prog_fb * RunAdjustment

			// "White"
			case "White":
				Query.Iteration_year_group[IterationNum][year]["White"]["USB"] += outputCS.Risk_of_prog_us * RunAdjustment
				Query.Iteration_year_group[IterationNum][year]["White"]["FB"] += outputCS.Risk_of_prog_fb * RunAdjustment

			// "Male"
			case "Male":
				Query.Iteration_year_group[IterationNum][year]["Male"]["USB"] += outputCS.Risk_of_prog_us * RunAdjustment
				Query.Iteration_year_group[IterationNum][year]["Male"]["FB"] += outputCS.Risk_of_prog_fb * RunAdjustment

			// "Female"
			case "Female":
				Query.Iteration_year_group[IterationNum][year]["Female"]["USB"] += outputCS.Risk_of_prog_us * RunAdjustment
				Query.Iteration_year_group[IterationNum][year]["Female"]["FB"] += outputCS.Risk_of_prog_fb * RunAdjustment

			}

			if outputCS.State_name == "Life" || outputCS.State_name == "Homeless" || outputCS.State_name == "Infected HIV, no ART" || outputCS.State_name == "Infected HIV, ART" || outputCS.State_name == "Diabetes" || outputCS.State_name == "ESRD" || outputCS.State_name == "Smoker" || outputCS.State_name == "Transplant patient" || outputCS.State_name == "TNF-alpha" || outputCS.State_name == "Asian" || outputCS.State_name == "Black" || outputCS.State_name == "Hispanic" || outputCS.State_name == "Other" || outputCS.State_name == "White" || outputCS.State_name == "Male" || outputCS.State_name == "Female" {

				var output_year_us OutputYear
				var output_year_fb OutputYear

				output_year_us.Year = year
				output_year_fb.Year = year

				output_year_us.CasesAllIterations += outputCS.Risk_of_prog_us * RunAdjustment
				output_year_fb.CasesAllIterations += outputCS.Risk_of_prog_fb * RunAdjustment

				output_year_us.CasesAverage += (outputCS.Risk_of_prog_us * RunAdjustment) / float64(NumberOfIterations)
				output_year_fb.CasesAverage += (outputCS.Risk_of_prog_fb * RunAdjustment) / float64(NumberOfIterations)

				output_year_us.Group = new_state_name
				output_year_fb.Group = new_state_name

				output_year_us.Nativity = "USB"
				output_year_fb.Nativity = "FB"

				Query.OutputYears = append(Query.OutputYears, output_year_us, output_year_fb)

			}

		}
	}

}

func printCalibToCsv() {

}

// finds the average of the runs
func compareToRvct() {

	data, err := ioutil.ReadFile("raw-data-files/rvct.yaml")
	check(err)

	err = yaml.Unmarshal([]byte(data), &Query.Year_group_avg_rvct)
	if err != nil {
		log.Fatalf("error: %v", err)
	}

	fmt.Println(Query.Year_group_avg_rvct)

}

func makeStratumHash(stratum_type_id uint, cycle Cycle, person Person) string {

	hash := ""
	//stratumType := Inputs.StratumTypes[stratum_type_id]
	//fmt.Println("statrum type id: ", stratum_type_id)
	chainIds := Query.Chain_ids_by_stratum_type_id[stratum_type_id]
	//fmt.Println("chain ids: ", chainIds)
	for _, chainId := range chainIds {
		chain := Inputs.Chains[chainId]
		stateName := person.get_state_by_chain(chain, cycle).Name
		hash = hash + "." + stateName
	}

	_ = hash
	//fmt.Println(hash)
	return hash

}

func runCyclePersonChain(cycleId uint, chainId uint, personId uint, isInitializationPhase bool) {

	cycle := Inputs.Cycles[cycleId]
	chain := Inputs.Chains[chainId]
	person := Inputs.People[personId]

	random := RandomController.nextPM(person.Id, chain.Id)

	// check to see if they have already been assigned a state for the next cycle
	mr := &Query.Master_record_next_cycle_by_person_and_chain[person.Id][chain.Id]
	// this is done by checking to see if the next cycle's master record has a
	// true "has entered simulation"
	if mr.Has_entered_simulation {
		// if so, skip this function by returning immediately.
		return
	}

	// get the current state of the person in this chain (should be
	// the uninitialized state for cycle 0)
	currentStateInThisChain := Inputs.States[Query.Master_record_current_cycle_by_person_and_chain[person.Id][chain.Id].State_id]

	// age everyone and increase time in US
	if chain.Id == AGE_CHAIN_ID { // only run this once per cycle
		Inputs.People[person.Id].Age = Inputs.People[person.Id].Age + (1.0 / 12.0)
		Inputs.People[person.Id].YearsInUs = Inputs.People[person.Id].YearsInUs + (1.0 / 12.0)
	}

	// groupApplies := make([]bool, len(Inputs.Interventions[InterventionId].Testing_groups), len(Inputs.Interventions[InterventionId].Testing_groups))
	monthly_testing_uptake := 0.0

	// ------- find if person qualifies for intervention

	// the first step is to see if they qualify, which means that they
	// meet the cirteria.
	if chain.Id == TB_CHAIN_ID && !isInitializationPhase {

		// they need to be in either fast latent, slow latent, or uninfected to qualify for testing
		if currentStateInThisChain.Id == SLOW_LATENT_ID ||
			currentStateInThisChain.Id == FAST_LATENT_ID ||
			currentStateInThisChain.Id == UNINF_ID {

			// first, assume they do not, which gives them the blank testing group
			Inputs.People[person.Id].TestingGroupId = 0
			were_criteria_met_for_fb := false

			for t, _ := range Inputs.Interventions[InterventionId].Testing_groups {

				numberOfCriteria := len(Inputs.Interventions[InterventionId].Testing_groups[t].Criteria)
				criteriaMet := 0
				for _, criteria := range Inputs.Interventions[InterventionId].Testing_groups[t].Criteria {
					xChain := Query.getChainByName(criteria.Chain_name)
					theirStateIdThisChain := person.get_state_by_chain(xChain, cycle)
					thisCriteriaMet := false
					for _, stateName := range criteria.State_names {
						if stateName == theirStateIdThisChain.Name {
							thisCriteriaMet = true
						}
					}
					if thisCriteriaMet {
						criteriaMet++
					}
				}
				if criteriaMet == numberOfCriteria && cycle.Id >= Inputs.Interventions[InterventionId].Testing_groups[t].Begin_cycle {

					// they have met the criteria. Now we roll to see if they
					// will actually be tested under this intervention
					monthly_testing_uptake = Inputs.Interventions[InterventionId].Testing_groups[t].Monthly_testing_uptake

					if t == 0 || t == 1 { // current effort interventions
						// only allowed one test per year
						if (cycle.Id-person.LastTbTest) < TbTestMonthCutoff && person.LastTbTest != 0 {
							monthly_testing_uptake = 0
						}
						// if they haven't had a TB test in 12 months and they are HCW, test them
						if (cycle.Id-person.LastTbTest) >= TbTestMonthCutoff && person.IsHcw {
							monthly_testing_uptake = 1
						}
					} else { // additional (non-current effort) interventions
						if Disallow_retest == 1 { // no retest
							if person.LastTbTest != 0 {
								monthly_testing_uptake = 0
							}
						} else { // allow re-test, expect within one year
							if (cycle.Id-person.LastTbTest) < TbTestMonthCutoff && person.LastTbTest != 0 {
								monthly_testing_uptake = 0
							}
						}
					}

					if Inputs.Interventions[InterventionId].Name == "2x in FB + Med risk factor (QFT/3HP)" || Inputs.Interventions[InterventionId].Name == "4x in FB + Med risk factor (QFT/3HP)" || Inputs.Interventions[InterventionId].Name == "10x in FB + Med risk factor (QFT/3HP)" {

						// checking to see if qualifies for "FB"
						if Inputs.Interventions[InterventionId].Testing_groups[t].Id == 3 {
							were_criteria_met_for_fb = true
						}

						// can't get twice coverage
						if Inputs.Interventions[InterventionId].Testing_groups[t].Id == 4 && were_criteria_met_for_fb {
							monthly_testing_uptake = 0
						}

					}

					rnd := RandomController.nextPM(person.Id, uint(t)) //just using t (testing group) as chain_id here, because just need a unique random float, should work

					// roll dice, see if they qualify for testing this cycle
					if rnd < monthly_testing_uptake {
						// if they do, assign testing group Id (0 = no group)
						Inputs.People[person.Id].LastTbTest = cycle.Id
						Inputs.People[person.Id].TestingGroupId = Inputs.Interventions[InterventionId].Testing_groups[t].Id
						// if person.Id < 100 {
						// 	fmt.Println("assigning", person.Id, " to ", Inputs.People[person.Id].TestingGroupId, " in cycle ", cycle.Id)
						// }
					}

				}

			}

		} // if fast/slow/ latent uninfected

	}

	// assign to the non-pointer so following doesn't neeed to refer to long
	// address to find testing group
	person.TestingGroupId = Inputs.People[person.Id].TestingGroupId

	// used for if intervention is only in Fb
	birthplaceStateId := Query.Master_record_current_cycle_by_person_and_chain[person.Id][BIRTHPLACE_CHAIN_ID].State_id

	isUsBorn := (birthplaceStateId == US_BIRTHPLACE_ID)
	riskOfInfection := 0.0

	// get the transition probabilities from the given state
	transitionProbabilities := getDestinationProbabilities(currentStateInThisChain.Id)

	// --------- Transition probability adjustments before interactions ----

	if chain.Id == TB_CHAIN_ID {
		for i, transitionProbability := range transitionProbabilities {

			// adjust Risk of progression based on nativity and race

			if transitionProbability.To_state_id == ACTIVE_UNTREATED_ID {

				// race
				switch Inputs.States[Query.Master_record_current_cycle_by_person_and_chain[person.Id][RACE_CHAIN_ID].State_id].Name {

				case "Asian":
					if isUsBorn {
						transitionProbabilities[i].Tp_base = transitionProbabilities[i].Tp_base * RopUsbAsianAdjustment.Value * 1.2 //1.1
					} else {
						transitionProbabilities[i].Tp_base = transitionProbabilities[i].Tp_base * RopFbAsianAdjustment.Value * 1.131764705 //* math.Pow(0.998, float64(cycle.Id)/12.0)
						// 1.5 //1.529411765
					}

				case "Black":
					if isUsBorn {
						transitionProbabilities[i].Tp_base = transitionProbabilities[i].Tp_base * RopUsbBlackAdjustment.Value * 1.615366542
					} else {
						transitionProbabilities[i].Tp_base = transitionProbabilities[i].Tp_base * RopFbBlackAdjustment.Value * 1.038461538 //2
					}

				case "Hispanic":
					if isUsBorn {
						transitionProbabilities[i].Tp_base = transitionProbabilities[i].Tp_base * RopUsbHispanicAdjustment.Value * 0.872836363
					} else {
						transitionProbabilities[i].Tp_base = transitionProbabilities[i].Tp_base * RopFbHispanicAdjustment.Value * 0.558409091
					}

				case "White":
					if isUsBorn {
						transitionProbabilities[i].Tp_base = transitionProbabilities[i].Tp_base * RopUsbWhiteAdjustment.Value * 1.988636362 * math.Pow(0.94, float64(cycle.Id)/12.0)
					} else {
						transitionProbabilities[i].Tp_base = transitionProbabilities[i].Tp_base * RopFbWhiteAdjustment.Value * 0.4
					}

				case "Other":
					if isUsBorn {
						transitionProbabilities[i].Tp_base = transitionProbabilities[i].Tp_base * RopUsbOtherAdjustment.Value * 0.277777778
					} else {
						transitionProbabilities[i].Tp_base = transitionProbabilities[i].Tp_base * RopFbOtherAdjustment.Value * 0.75
					}
				}

				// diabetes
				dmStateName := Inputs.States[Query.Master_record_current_cycle_by_person_and_chain[person.Id][DIABETES_CHAIN_ID].State_id].Name
				if dmStateName == "Diabetes" && !isUsBorn {
					transitionProbabilities[i].Tp_base = transitionProbabilities[i].Tp_base * 1.3 * 1.15 * 1.15 //RopFbDmAdjustment.Value
				}

				// sex
				sexStateName := Inputs.States[Query.Master_record_current_cycle_by_person_and_chain[person.Id][SEX_CHAIN_ID].State_id].Name

				// FB
				if sexStateName == "Male" && !isUsBorn {
					transitionProbabilities[i].Tp_base = transitionProbabilities[i].Tp_base * 1.153846154
				} else if sexStateName == "Female" && !isUsBorn {
					transitionProbabilities[i].Tp_base = transitionProbabilities[i].Tp_base * 0.833333333
				}

				// USB
				if isUsBorn {
					transitionProbabilities[i].Tp_base = transitionProbabilities[i].Tp_base * 1.05
				}

				lotStateName := Inputs.States[Query.Master_record_current_cycle_by_person_and_chain[person.Id][LEN_TIME_CHAIN_ID].State_id].Name
				// "imported" active cases
				if lotStateName == "Less than one year" && (currentStateInThisChain.Name == "Slow latent" || currentStateInThisChain.Name == "Fast latent") {
					if cycle.Id < 13 {
						transitionProbabilities[i].Tp_base = transitionProbabilities[i].Tp_base + 0.0011
					} else if cycle.Id < 25 && cycle.Id > 12 {
						transitionProbabilities[i].Tp_base = transitionProbabilities[i].Tp_base + 0.0015
					} else {
						transitionProbabilities[i].Tp_base = transitionProbabilities[i].Tp_base + 0.002*math.Pow(1.0-0.008, float64(cycle.Id))
					}

				}

				//
			}

			// adjust TST for FB  ------ assume all FBs have BCG -- implemented with stratification system now

			// if !isUsBorn && Inputs.States[transitionProbability.From_state_id].Id == UNINF_TESTING_TST_ID &&
			// 	(Inputs.States[transitionProbability.To_state_id].Id == FP_LBTI_9M_INH ||
			// 		Inputs.States[transitionProbability.To_state_id].Id == FP_LTBI_6M_INH ||
			// 		Inputs.States[transitionProbability.To_state_id].Id == FP_LTBI_RIF ||
			// 		Inputs.States[transitionProbability.To_state_id].Id == FP_LTBI_RTP) {
			// 	transitionProbabilities[i].Tp_base = (1.0 - TstSpecificityBcgVaccinated.Value) * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveTstLtbiTest.Value
			// }

			// TO DO Recent transmission --------------!!!!!!!!!!!!!!!!

			// ----------- Recent transmmission -------------
			// Increase risk of progression for those with recent infection

			if transitionProbabilities[i].To_state_id == ACTIVE_UNTREATED_ID && !isInitializationPhase &&
				currentStateInThisChain.Name != "Death" &&
				currentStateInThisChain.Name != "Active - untreated" &&
				currentStateInThisChain.Name != "Active Treated Month 1" &&
				currentStateInThisChain.Name != "Active Treated Month 2" &&
				currentStateInThisChain.Name != "Active Treated Month 3" &&
				currentStateInThisChain.Name != "Active Treated Month 4" &&
				currentStateInThisChain.Name != "Active Treated Month 5" &&
				currentStateInThisChain.Name != "Active Treated Month 6" &&
				currentStateInThisChain.Name != "Default" &&
				currentStateInThisChain.Name != "Former active TB" &&
				currentStateInThisChain.Name != "LTBI treated with INH 9m" &&
				currentStateInThisChain.Name != "LTBI treated with INH 6m" &&
				currentStateInThisChain.Name != "LTBI treated with RIF" &&
				currentStateInThisChain.Name != "LTBI treated with RTP" {
				if person.MonthsSinceTBInfection < 36 {
					// fmt.Println("person has ", person.MonthsSinceTBInfection, " months of infection. Adjusting TP by ", RecentInfectionAdjustment)
					transitionProbabilities[i].Tp_base = transitionProbabilities[i].Tp_base * RecentInfectionAdjustment
				}
			}

			// ----------------- Intervention : testing

			if !isInitializationPhase &&
				(transitionProbability.To_state_id == INF_TST_ID ||
					transitionProbability.To_state_id == INF_QFT_ID ||
					transitionProbability.To_state_id == INF_TSPOT_ID ||
					transitionProbability.To_state_id == INF_TST_QFT_ID ||
					transitionProbability.To_state_id == INF_TST_TSPOT_ID ||
					transitionProbability.To_state_id == UNI_TST_ID ||
					transitionProbability.To_state_id == UNI_QFT_ID ||
					transitionProbability.To_state_id == UNI_TSPOT_ID ||
					transitionProbability.To_state_id == UNI_TST_QFT_ID ||
					transitionProbability.To_state_id == UNI_TST_TSPOT_ID) {

				// they were assigned a testing group
				if person.TestingGroupId != 0 {
					testing_group := Inputs.Interventions[InterventionId].Testing_groups[person.TestingGroupId-1]
					if cycle.Id < testing_group.End_cycle && cycle.Id >= testing_group.Begin_cycle {
						// determine test for this test group
						testing_choice_neg_id := Query.getStateByName(testing_group.Test_choice_neg).Id
						testing_choice_pos_id := Query.getStateByName(testing_group.Test_choice_pos).Id

						if transitionProbability.To_state_id == testing_choice_neg_id || transitionProbability.To_state_id == testing_choice_pos_id {
							transitionProbabilities[i].Tp_base = 0.95
						} else {
							transitionProbabilities[i].Tp_base = 0
						}
					}
				} else {
					//they were not assigned a testing group
					transitionProbabilities[i].Tp_base = 0
				}

			}

			// ---------------- Transmission

			if transitionProbability.Is_dynamic {

				funcName := transitionProbability.Dynamic_function_name

				switch funcName {

				case "TB trans to fast latent":
					isUsb := 0
					if person.get_state_by_chain(Inputs.Chains[BIRTHPLACE_CHAIN_ID], cycle).Name == "United States" {
						isUsb = 1
					}

					race_state_id := Query.Master_record_current_cycle_by_person_and_chain[person.Id][RACE_CHAIN_ID].State_id

					riskOfInfection = Query.LTBI_risk_by_cycle_isUsb_and_race[cycle.Id][isUsb][race_state_id]

					//xyx

					if isUsb == 1 {
						transitionProbabilities[i].Tp_base = riskOfInfection * 1.0 * math.Pow(0.975, float64(cycle.Id)/12.0) // .975 -> .985 all go to fast latent  //3.7 & .8
					} else {
						if cycle.Id < 85 {
							transitionProbabilities[i].Tp_base = riskOfInfection * 1.0 * math.Pow(0.999, float64(cycle.Id)/12.0)
						} else {
							transitionProbabilities[i].Tp_base = riskOfInfection * 1.0 * math.Pow(0.99, float64(cycle.Id)/12.0) //99
						}
					}

					// if they have been here for less than one year, I give them immunity from recent transmission; otherwise it
					// messes everything up because then they have an extremely high risk of reactivation

					if person.get_state_by_chain(Query.getChainByName("Length of time in US"), cycle).Name == "Less than one year" {
						transitionProbabilities[i].Tp_base = 0
					}

				}

			}

			// ------ if any adjustments were applied to TPs and they were stratifed,
			// they are removed. would be good to check to see if this is OK!

			// if the transition probability is stratified, find what stratum they
			// are in, and find the TP for that straum

		}
	}

	// -- Non-TB TP adjustments

	if Query.State_id_has_stratified_tp[currentStateInThisChain.Id] {
		for i, transitionProbability := range transitionProbabilities {
			if transitionProbability.Is_stratified {
				stratum_type_id := transitionProbability.Stratum_type_id
				stratum_hash := makeStratumHash(stratum_type_id, cycle, person)
				stratum_id := Query.Stratum_id_by_hash[stratum_hash]

				tp_by_stratum_id := Query.Tp_stratum_id_by_tp_and_stratum[transitionProbability.Id][stratum_id]
				tp_by_stratum := Inputs.TransitionProbabilitiesByStratum[tp_by_stratum_id]
				if tp_by_stratum.From_state_id != currentStateInThisChain.Id {
					fmt.Println("Cannot find TP by stratum")
					fmt.Println(transitionProbability, stratum_hash)
					os.Exit(1)
				}

				value := tp_by_stratum.Base
				transitionProbabilities[i].Tp_base = value

				// if isInitializationPhase && cycle.Id < 1 && chain.Name == "TB disease and treatment" && Inputs.States[transitionProbabilities[i].To_state_id].Name == "Fast latent" {

				// 	fmt.Println(stratum_hash, value)

				// }

			}
		}
	}

	// ---------------- Treatment
	// now that transitions to treatment is a stratified TP, these adjustments
	// need to come after the stratifed variables are pulled

	if chain.Id == TB_CHAIN_ID {
		for i, transitionProbability := range transitionProbabilities {
			if !isInitializationPhase &&
				(transitionProbability.To_state_id == LBTI_9M_INH ||
					transitionProbability.To_state_id == LTBI_6M_INH ||
					transitionProbability.To_state_id == LTBI_RIF ||
					transitionProbability.To_state_id == LTBI_RTP ||
					transitionProbability.To_state_id == FP_LBTI_9M_INH ||
					transitionProbability.To_state_id == FP_LTBI_6M_INH ||
					transitionProbability.To_state_id == FP_LTBI_RIF ||
					transitionProbability.To_state_id == FP_LTBI_RTP) {

				if person.TestingGroupId != 0 {
					testing_group := Inputs.Interventions[InterventionId].Testing_groups[person.TestingGroupId-1]
					// determine treatment for this test group
					treatment_choice_neg_id := Query.getStateByName(testing_group.Treatment_choice_neg).Id
					treatment_choice_pos_id := Query.getStateByName(testing_group.Treatment_choice_pos).Id
					if transitionProbability.To_state_id == treatment_choice_neg_id ||
						transitionProbability.To_state_id == treatment_choice_pos_id {
						// do nothing
					} else {
						transitionProbabilities[i].Tp_base = 0
					}
				} else {
					transitionProbabilities[i].Tp_base = 0
				}
			}
		}
	}

	// if sum doesn't equal one, adjust as needed
	sum := get_sum(transitionProbabilities)
	if !equalFloat(sum, 1.0, 0.00000001) {
		transitionProbabilities = adjust_tps_over_one(transitionProbabilities)
	}

	// will throw error if sum isn't 1
	check_sum(transitionProbabilities, "after strat")

	// ------------ Interactions ----------------

	hivStateId := Query.Master_record_current_cycle_by_person_and_chain[person.Id][HIV_CHAIN_ID].State_id
	diabetesStateId := Query.Master_record_current_cycle_by_person_and_chain[person.Id][DIABETES_CHAIN_ID].State_id
	homeslessnessStateId := Query.Master_record_current_cycle_by_person_and_chain[person.Id][HOMESLESSNESS_CHAIN_ID].State_id
	esrdStateId := Query.Master_record_current_cycle_by_person_and_chain[person.Id][ESRD_CHAIN_ID].State_id
	tnfStateId := Query.Master_record_current_cycle_by_person_and_chain[person.Id][TNF_CHAIN_ID].State_id
	smokerStateId := Query.Master_record_current_cycle_by_person_and_chain[person.Id][SMOKER_CHAIN_ID].State_id
	transplantsStateId := Query.Master_record_current_cycle_by_person_and_chain[person.Id][TRANSPLANTS_CHAIN_ID].State_id

	// increase risk of progression for those with medical risk factors
	if chain.Id == TB_CHAIN_ID {
		for i, tp := range transitionProbabilities {
			if tp.To_state_id == ACTIVE_UNTREATED_ID {

				adjustment := 1.0

				if hivStateId == INFECTEDHIVART_STATE_ID || hivStateId == INFECTEDHIVNOART_STATE_ID {
					adjustment = adjustment * 12.0
				}

				if smokerStateId == SMOKER_STATE_ID {
					adjustment = adjustment * 2.5
				}
				if esrdStateId == ESRD_STATE_ID {
					adjustment = adjustment * 11.0
				}
				if tnfStateId == TNFALPHA_STATE_ID {
					adjustment = adjustment * 6.0 //4.7
				}
				if diabetesStateId == DIABETES_STATE_ID {
					adjustment = adjustment * 1.6
				}

				if transplantsStateId == TRANSPLANTPATIENT_STATE_ID {
					adjustment = adjustment * 2.4 * 2.0
				}

				transitionProbabilities[i].Tp_base = transitionProbabilities[i].Tp_base * adjustment
				if transitionProbabilities[i].Tp_base > 1 {
					transitionProbabilities[i].Tp_base = 1
				}

			}

		}

	}

	// diabetics more likely to get ESRD
	if chain.Id == ESRD_CHAIN_ID {
		for i, tp := range transitionProbabilities {
			if Inputs.States[tp.To_state_id].Name == "ESRD" && Inputs.States[tp.From_state_id].Name == "No ESRD" && diabetesStateId == DIABETES_STATE_ID {
				transitionProbabilities[i].Tp_base = transitionProbabilities[i].Tp_base * 10.4
			}
			if transitionProbabilities[i].Tp_base > 1 {
				transitionProbabilities[i].Tp_base = 1
			}
		}
	}

	// older people more likely to use TNF-alpha
	if chain.Id == TNF_CHAIN_ID {
		age_state_id := Query.Master_record_current_cycle_by_person_and_chain[person.Id][AGE_CHAIN_ID].State_id
		age_state_name := Inputs.States[age_state_id].Name
		for i, tp := range transitionProbabilities {
			if Inputs.States[tp.To_state_id].Name == "TNF-alpha" && Inputs.States[tp.From_state_id].Name == "No TNF-alpha" {
				switch age_state_name {
				case "Age 35-39":
					transitionProbabilities[i].Tp_base = transitionProbabilities[i].Tp_base * 4.16091954
				case "Age 40-44":
					transitionProbabilities[i].Tp_base = transitionProbabilities[i].Tp_base * 4.16091954
				case "Age 45-49":
					transitionProbabilities[i].Tp_base = transitionProbabilities[i].Tp_base * 5.16091954
				case "Age 50-54":
					transitionProbabilities[i].Tp_base = transitionProbabilities[i].Tp_base * 5.16091954
				case "Age 55-59":
					transitionProbabilities[i].Tp_base = transitionProbabilities[i].Tp_base * 7.275862069
				case "Age 60-64":
					transitionProbabilities[i].Tp_base = transitionProbabilities[i].Tp_base * 7.275862069
				case "Age 65-69":
					transitionProbabilities[i].Tp_base = transitionProbabilities[i].Tp_base * 10.27586207
				case "Age 70-74":
					transitionProbabilities[i].Tp_base = transitionProbabilities[i].Tp_base * 10.27586207
				case "Age 75-79":
					transitionProbabilities[i].Tp_base = transitionProbabilities[i].Tp_base * 7.988505747
				case "Age 80+":
					transitionProbabilities[i].Tp_base = transitionProbabilities[i].Tp_base * 6.149425287
				}
			}
		}
	}

	// SMRs
	if chain.Name == "Natural death" {
		for i, tp := range transitionProbabilities {
			if Inputs.States[tp.To_state_id].Name == "Death" {

				adjustment := 1.0

				if hivStateId == INFECTEDHIVART_STATE_ID {
					adjustment = adjustment * 1.24
				}
				if hivStateId == INFECTEDHIVNOART_STATE_ID {
					adjustment = adjustment * 5.6
				}
				if smokerStateId == SMOKER_STATE_ID {
					adjustment = adjustment * 1.8
				}
				if esrdStateId == ESRD_STATE_ID {
					adjustment = adjustment * 5.9
				}
				if tnfStateId == TNF_CHAIN_ID {
					adjustment = adjustment * 1.41
				}
				if diabetesStateId == DIABETES_STATE_ID {
					adjustment = adjustment * 3.0
				}
				if transplantsStateId == TRANSPLANTPATIENT_STATE_ID {
					adjustment = adjustment * 15.0
				}
				transitionProbabilities[i].Tp_base = transitionProbabilities[i].Tp_base * adjustment

			}
			if transitionProbabilities[i].Tp_base > 1 {
				transitionProbabilities[i].Tp_base = 1
			}

		}

	}

	// if sum doesn't equal one, adjust as needed
	sum = get_sum(transitionProbabilities)
	if !equalFloat(sum, 1.0, 0.00000001) {
		transitionProbabilities = adjust_tps_over_one(transitionProbabilities)
	}

	// will throw error if sum isn't 1
	check_sum(transitionProbabilities, "after interactions")

	//   ------------------------ calibration yyy  ------------------------

	//------ of smoking to set old smoking rates (could be moved up)

	if chain.Id == SMOKER_CHAIN_ID {

		for i := 0; i < len(transitionProbabilities); i++ {

			if RunType == "calib" && cycle.Id < 1 {
				if Inputs.States[transitionProbabilities[i].From_state_id].Name == "Uninitialized" && Inputs.States[transitionProbabilities[i].To_state_id].Name == "Smoker" {
					// fmt.Println("adjusting for smoking. tp was", transitionProbabilities[i].Tp_base)
					transitionProbabilities[i].Tp_base = transitionProbabilities[i].Tp_base * 1.17 //1.25 //1.22 //1.2 // 1.3
					// fmt.Println("tp now", transitionProbabilities[i].Tp_base)
				}
				if Inputs.States[transitionProbabilities[i].From_state_id].Name == "Uninitialized" && Inputs.States[transitionProbabilities[i].To_state_id].Name == "Non-smoker" {
					transitionProbabilities[i].Tp_base = 1.0 - ((1.0 - transitionProbabilities[i].Tp_base) * 1.17) //1.25) //1.22 //1.2 //1.3
				}
			}

		}
	}

	/// -------------- outmigration by race and nativity

	outmigration := 0.001488095

	switch Inputs.States[Query.Master_record_current_cycle_by_person_and_chain[person.Id][RACE_CHAIN_ID].State_id].Name {

	case "Asian":
		if isUsBorn {
			outmigration = outmigration * 0.9
		} else {
			outmigration = outmigration * 0.85 //0.9
		}
	case "Black":
		if isUsBorn {
			outmigration = outmigration * 0.9
		} else {
			outmigration = outmigration * 1.3
		}
	case "Hispanic":
		if isUsBorn {
			outmigration = outmigration * 0.84 //.9 //1.0
		} else {
			outmigration = outmigration * 0.45 //0.1
		}
	case "White":
		if isUsBorn {
			outmigration = outmigration * 1.2
		} else {
			outmigration = outmigration * 1.1
		}
	case "Other":
		if isUsBorn {
			outmigration = outmigration * 1.0
		} else {
			outmigration = outmigration * 1.0
		}
	}

	// -------------------------- Natural death

	if !isInitializationPhase && chain.Name == "Natural death" {

		for q := 0; q < len(transitionProbabilities); q++ {
			if Inputs.States[transitionProbabilities[q].From_state_id].Name == "Life" && Inputs.States[transitionProbabilities[q].To_state_id].Name == "Death" {
				transitionProbabilities[q].Tp_base = transitionProbabilities[q].Tp_base + outmigration // this represents outmigration for now
			}
		}
	}

	// -------------------------- HIV prev

	if chain.Id == HIV_CHAIN_ID {

		hivAdjustment := 1.0
		if cycle.Id < 1 {
			hivAdjustment = 1.667268728
		} else {
			hivAdjustment = 1.667268728
		}
		if isInitializationPhase && cycle.Id < 1 && chain.Name == "HIV" {
			var noArtChance float64
			var artChance float64
			var uninfectedChance float64
			for q := 0; q < len(transitionProbabilities); q++ {
				// no ART
				if Inputs.States[transitionProbabilities[q].From_state_id].Name == "Uninitialized" && Inputs.States[transitionProbabilities[q].To_state_id].Name == "Infected HIV, no ART" {
					noArtChance = transitionProbabilities[q].Tp_base
				}
				// with ART
				if Inputs.States[transitionProbabilities[q].From_state_id].Name == "Uninitialized" && Inputs.States[transitionProbabilities[q].To_state_id].Name == "Infected HIV, ART" {
					artChance = transitionProbabilities[q].Tp_base
				}
				if Inputs.States[transitionProbabilities[q].From_state_id].Name == "Uninitialized" && Inputs.States[transitionProbabilities[q].To_state_id].Name == "Uninfected HIV" {
					uninfectedChance = transitionProbabilities[q].Tp_base
				}
			}
			// apply

			for q := 0; q < len(transitionProbabilities); q++ {
				// no ART
				if Inputs.States[transitionProbabilities[q].From_state_id].Name == "Uninitialized" && Inputs.States[transitionProbabilities[q].To_state_id].Name == "Infected HIV, no ART" {
					transitionProbabilities[q].Tp_base = noArtChance * hivAdjustment
				}
				// with ART
				if Inputs.States[transitionProbabilities[q].From_state_id].Name == "Uninitialized" && Inputs.States[transitionProbabilities[q].To_state_id].Name == "Infected HIV, ART" {
					transitionProbabilities[q].Tp_base = artChance * hivAdjustment
				}
				if Inputs.States[transitionProbabilities[q].From_state_id].Name == "Uninitialized" && Inputs.States[transitionProbabilities[q].To_state_id].Name == "Uninfected HIV" {
					transitionProbabilities[q].Tp_base = uninfectedChance - artChance*(hivAdjustment-1) - noArtChance*(hivAdjustment-1)
				}
			} // end loop
		}
	}

	// -------------------------- tnf

	// --- initialization

	if isInitializationPhase && cycle.Id < 1 && chain.Name == "TNF-alpha" {

		tnfAdjustment := 1.0
		if cycle.Id < 1 {
			if isUsBorn {
				tnfAdjustment = 2
			} else {
				tnfAdjustment = 2
			}
		}
		var tnfChance float64
		var notnfchance float64
		for q := 0; q < len(transitionProbabilities); q++ {
			if Inputs.States[transitionProbabilities[q].From_state_id].Name == "Uninitialized" && Inputs.States[transitionProbabilities[q].To_state_id].Name == "TNF-alpha" {
				tnfChance = transitionProbabilities[q].Tp_base
			}
			if Inputs.States[transitionProbabilities[q].From_state_id].Name == "Uninitialized" && Inputs.States[transitionProbabilities[q].To_state_id].Name == "No TNF-alpha" {
				notnfchance = transitionProbabilities[q].Tp_base
			}
		}
		// apply
		for q := 0; q < len(transitionProbabilities); q++ {
			if Inputs.States[transitionProbabilities[q].From_state_id].Name == "Uninitialized" && Inputs.States[transitionProbabilities[q].To_state_id].Name == "TNF-alpha" {
				transitionProbabilities[q].Tp_base = tnfChance * tnfAdjustment
			}
			if Inputs.States[transitionProbabilities[q].From_state_id].Name == "Uninitialized" && Inputs.States[transitionProbabilities[q].To_state_id].Name == "No TNF-alpha" {
				transitionProbabilities[q].Tp_base = notnfchance - tnfChance*(tnfAdjustment-1)
			}
		}

	}

	// -------------------------- tnf incidence
	if !isInitializationPhase && chain.Name == "TNF-alpha" {
		// --- incidence
		for q := 0; q < len(transitionProbabilities); q++ {
			if Inputs.States[transitionProbabilities[q].From_state_id].Name == "No TNF-alpha" && Inputs.States[transitionProbabilities[q].To_state_id].Name == "TNF-alpha" {
				transitionProbabilities[q].Tp_base = transitionProbabilities[q].Tp_base * 2.0 //0.55 //looks great
			}
		}
	}

	// -------------------------- transplants

	// --- initialization

	if isInitializationPhase && cycle.Id < 1 && chain.Name == "Transplants" {

		transplantAdjustment := 1.0
		if cycle.Id < 1 {
			if isUsBorn {
				transplantAdjustment = 1.0
			} else {
				transplantAdjustment = 1.0
			}
		}

		var transplantChance float64
		var noTransplantChance float64
		for q := 0; q < len(transitionProbabilities); q++ {
			if Inputs.States[transitionProbabilities[q].From_state_id].Name == "Uninitialized" && Inputs.States[transitionProbabilities[q].To_state_id].Name == "Transplant patient" {
				transplantChance = transitionProbabilities[q].Tp_base
			}
			if Inputs.States[transitionProbabilities[q].From_state_id].Name == "Uninitialized" && Inputs.States[transitionProbabilities[q].To_state_id].Name == "Not transplant patient" {
				noTransplantChance = transitionProbabilities[q].Tp_base
			}
		}
		// apply
		for q := 0; q < len(transitionProbabilities); q++ {
			if Inputs.States[transitionProbabilities[q].From_state_id].Name == "Uninitialized" && Inputs.States[transitionProbabilities[q].To_state_id].Name == "Transplant patient" {
				transitionProbabilities[q].Tp_base = transplantChance * transplantAdjustment
			}
			if Inputs.States[transitionProbabilities[q].From_state_id].Name == "Uninitialized" && Inputs.States[transitionProbabilities[q].To_state_id].Name == "Not transplant patient" {
				transitionProbabilities[q].Tp_base = noTransplantChance - transplantChance*(transplantAdjustment-1)
			}
		}

	}

	// -------------------------- diabetes

	// --- initialization

	if isInitializationPhase && cycle.Id < 1 && chain.Id == DIABETES_CHAIN_ID {

		dmAdjustment := 1.0
		if cycle.Id < 1 {
			if isUsBorn {
				dmAdjustment = 0.83 //looks great
			} else {
				dmAdjustment = 1.12 //looks great
			}
		}
		var dmChance float64
		var uninfectedChance float64
		for q := 0; q < len(transitionProbabilities); q++ {
			if Inputs.States[transitionProbabilities[q].From_state_id].Name == "Uninitialized" && Inputs.States[transitionProbabilities[q].To_state_id].Name == "Diabetes" {
				dmChance = transitionProbabilities[q].Tp_base
			}
			if Inputs.States[transitionProbabilities[q].From_state_id].Name == "Uninitialized" && Inputs.States[transitionProbabilities[q].To_state_id].Name == "No diabetes" {
				uninfectedChance = transitionProbabilities[q].Tp_base
			}
		}
		// apply
		for q := 0; q < len(transitionProbabilities); q++ {
			if Inputs.States[transitionProbabilities[q].From_state_id].Name == "Uninitialized" && Inputs.States[transitionProbabilities[q].To_state_id].Name == "Diabetes" {
				transitionProbabilities[q].Tp_base = dmChance * dmAdjustment
			}
			if Inputs.States[transitionProbabilities[q].From_state_id].Name == "Uninitialized" && Inputs.States[transitionProbabilities[q].To_state_id].Name == "No diabetes" {
				transitionProbabilities[q].Tp_base = uninfectedChance - dmChance*(dmAdjustment-1)
			}
		}

	}
	if !isInitializationPhase && chain.Id == DIABETES_CHAIN_ID {
		// --- incidence
		for q := 0; q < len(transitionProbabilities); q++ {
			if Inputs.States[transitionProbabilities[q].From_state_id].Name == "No diabetes" && Inputs.States[transitionProbabilities[q].To_state_id].Name == "Diabetes" {
				transitionProbabilities[q].Tp_base = transitionProbabilities[q].Tp_base * 0.85
			}
		}
	}

	// -------------------------- esrd

	// --- initialization

	if isInitializationPhase && cycle.Id < 1 && chain.Name == "ESRD" {
		esrdAdjustment := 1.0
		if cycle.Id < 1 {
			esrdAdjustment = 0.9 //1 //0.8 //0.69
		}
		var esrdChance float64
		var uninfectedChance float64
		for q := 0; q < len(transitionProbabilities); q++ {
			if Inputs.States[transitionProbabilities[q].From_state_id].Name == "Uninitialized" && Inputs.States[transitionProbabilities[q].To_state_id].Name == "ESRD" {
				esrdChance = transitionProbabilities[q].Tp_base
			}
			if Inputs.States[transitionProbabilities[q].From_state_id].Name == "Uninitialized" && Inputs.States[transitionProbabilities[q].To_state_id].Name == "No ESRD" {
				uninfectedChance = transitionProbabilities[q].Tp_base
			}
		}
		// apply
		for q := 0; q < len(transitionProbabilities); q++ {
			if Inputs.States[transitionProbabilities[q].From_state_id].Name == "Uninitialized" && Inputs.States[transitionProbabilities[q].To_state_id].Name == "ESRD" {
				transitionProbabilities[q].Tp_base = esrdChance * esrdAdjustment
			}
			if Inputs.States[transitionProbabilities[q].From_state_id].Name == "Uninitialized" && Inputs.States[transitionProbabilities[q].To_state_id].Name == "No ESRD" {
				transitionProbabilities[q].Tp_base = uninfectedChance - esrdChance*(esrdAdjustment-1)
			}
		}

	}
	if !isInitializationPhase && chain.Name == "ESRD" {
		// --- incidence
		for q := 0; q < len(transitionProbabilities); q++ {
			if Inputs.States[transitionProbabilities[q].From_state_id].Name == "No ESRD" && Inputs.States[transitionProbabilities[q].To_state_id].Name == "ESRD" {
				transitionProbabilities[q].Tp_base = transitionProbabilities[q].Tp_base * 1.4
			}
		}
	}

	// -------------------------- smoking incidence
	if !isInitializationPhase && chain.Name == "Smoking" {
		// --- incidence
		for q := 0; q < len(transitionProbabilities); q++ {
			if Inputs.States[transitionProbabilities[q].From_state_id].Name == "Smoker" && Inputs.States[transitionProbabilities[q].To_state_id].Name == "Non-smoker" {
				transitionProbabilities[q].Tp_base = transitionProbabilities[q].Tp_base * 0.5 //0.55 //looks great
			}
		}
	}

	// --- starting LTBI prevalence

	finalAdjustmentFastLatent := 1.0
	finalAdjustmentSlowLatent := 1.0
	//finalAdjustmentTreated := 1.0

	if isInitializationPhase && chain.Name == "TB disease and treatment" {

		// overall ltbi adjustment
		finalAdjustment := LtbiOverallAdjustmentStarting.Value

		// fb and us born adjustment
		if isUsBorn {
			finalAdjustment = finalAdjustment * LtbiOverallUsbAdjustmentStarting.Value
		} else {
			finalAdjustment = finalAdjustment * LtbiOverallFbAdjustmentStarting.Value
		}

		if !isUsBorn {
			finalAdjustment = finalAdjustment * math.Pow(0.982, float64(cycle.Id)/12.0)
		}

		finalAdjustmentFastLatent = finalAdjustment
		finalAdjustmentSlowLatent = finalAdjustment

		//xyx

		if cycle.Id == 0 && isUsBorn {
			finalAdjustmentFastLatent = 2.9
		} else if cycle.Id == 0 && !isUsBorn {
			finalAdjustmentFastLatent = 0.875 * 1.147058824 * 0.875 //0.75
		} else {
			// to do - FB people should be able to enter
			finalAdjustmentFastLatent = 0
		}

		/// --------  apply

		var slowLatentChance float64
		var fastLatentChance float64
		var uninfectedChance float64
		var treatedChance float64

		// find the tp to fast latent and slow latent

		for q := 0; q < len(transitionProbabilities); q++ {

			// slow latent
			if Inputs.States[transitionProbabilities[q].From_state_id].Name == "Uninitialized" && Inputs.States[transitionProbabilities[q].To_state_id].Name == "Slow latent" {
				// fmt.Println("here!", person.get_state_by_chain(Query.getChainByName("Race"), cycle).Name)
				slowLatentChance = transitionProbabilities[q].Tp_base
			}

			if Inputs.States[transitionProbabilities[q].From_state_id].Name == "Uninitialized" && Inputs.States[transitionProbabilities[q].To_state_id].Name == "Fast latent" {
				fastLatentChance = transitionProbabilities[q].Tp_base
			}

			if Inputs.States[transitionProbabilities[q].From_state_id].Name == "Uninitialized" && Inputs.States[transitionProbabilities[q].To_state_id].Name == "Uninfected TB" {
				uninfectedChance = transitionProbabilities[q].Tp_base

			}

			if Inputs.States[transitionProbabilities[q].From_state_id].Name == "Uninitialized" && Inputs.States[transitionProbabilities[q].To_state_id].Name == "LTBI treated with INH 6m" {
				treatedChance = transitionProbabilities[q].Tp_base

			}

		} // end loop

		// if they have been here for less than one year, I give them immunity from recent transmission (fast latent); otherwise it
		// messes everything up because then they have an extremely high risk of reactivation

		if Inputs.States[Query.Master_record_current_cycle_by_person_and_chain[person.Id][LEN_TIME_CHAIN_ID].State_id].Name == "Less than one year" {
			fastLatentChance = 0
		}

		_ = uninfectedChance

		if cycle.Id == 0 && isUsBorn {
			treatedChance = 0.18 * slowLatentChance
		} else if cycle.Id == 0 && !isUsBorn {
			treatedChance = 0.12 * slowLatentChance
		} else {
			treatedChance = 0
		}

		// apply

		var new_slowLatentChance float64
		var new_fastLatentChance float64
		var new_uninfectedChance float64
		var new_treatedChance float64

		for i := 0; i < len(transitionProbabilities); i++ {

			if Inputs.States[transitionProbabilities[i].From_state_id].Name == "Uninitialized" && Inputs.States[transitionProbabilities[i].To_state_id].Name == "Fast latent" {

				transitionProbabilities[i].Tp_base = fastLatentChance * finalAdjustmentFastLatent
				new_fastLatentChance = transitionProbabilities[i].Tp_base

			}
			if Inputs.States[transitionProbabilities[i].From_state_id].Name == "Uninitialized" && Inputs.States[transitionProbabilities[i].To_state_id].Name == "Slow latent" {

				transitionProbabilities[i].Tp_base = slowLatentChance * finalAdjustmentSlowLatent
				new_slowLatentChance = transitionProbabilities[i].Tp_base
			}

			if Inputs.States[transitionProbabilities[i].From_state_id].Name == "Uninitialized" && Inputs.States[transitionProbabilities[i].To_state_id].Name == "LTBI treated with INH 6m" {

				transitionProbabilities[i].Tp_base = treatedChance
				new_treatedChance = transitionProbabilities[i].Tp_base
			}

			if Inputs.States[transitionProbabilities[i].From_state_id].Name == "Uninitialized" && Inputs.States[transitionProbabilities[i].To_state_id].Name == "Uninfected TB" {

				transitionProbabilities[i].Tp_base = 1.0 - slowLatentChance*(finalAdjustmentSlowLatent) - fastLatentChance*(finalAdjustmentFastLatent) - treatedChance
				new_uninfectedChance = transitionProbabilities[i].Tp_base
			}

		}

		newSum := new_slowLatentChance + new_fastLatentChance + new_uninfectedChance + new_treatedChance
		if !equalFloat(newSum, 1.0, 0.00000001) {
			fmt.Println("slowLatentChance ", "fastLatentChance ", "uninfectedChance ", "treatedChance ", new_slowLatentChance, new_fastLatentChance, new_uninfectedChance, new_treatedChance)
			fmt.Println("Oh no, ", newSum)
			os.Exit(1)
		}

	}
	// -------------- risk of progression --------------------
	// TODO: there is a problem here - it calculates ROP for next cycle based on this cycle
	// instead, we should save in the old cycle.
	// shouldn't make a big difference

	riskOfProgression := 0.0

	if chain.Id == TB_CHAIN_ID {

		// find TP to active disease
		if !currentStateInThisChain.Is_uninitialized_state &&
			currentStateInThisChain.Id != ACTIVE_UNTREATED_ID &&
			currentStateInThisChain.Id != ACTIVE_TREATED_M1_ID &&
			currentStateInThisChain.Id != ACTIVE_TREATED_M2_ID &&
			currentStateInThisChain.Id != ACTIVE_TREATED_M3_ID &&
			currentStateInThisChain.Id != ACTIVE_TREATED_M4_ID &&
			currentStateInThisChain.Id != ACTIVE_TREATED_M5_ID &&
			currentStateInThisChain.Id != ACTIVE_TREATED_M6_ID &&
			currentStateInThisChain.Id != DEFAULT_ID {

			for i, tp := range transitionProbabilities {
				if tp.To_state_id == ACTIVE_UNTREATED_ID {

					// CALIBRATION ADJUSTMENT TODO
					// transitionProbabilities[i].Tp_base = transitionProbabilities[i].Tp_base * 0.82

					riskOfProgression = transitionProbabilities[i].Tp_base
					if riskOfProgression > 1 {
						fmt.Println("Risk of progression cannot be more than one")
						os.Exit(1)
					}
					Inputs.People[person.Id].RiskOfProgression = riskOfProgression
				}
			}
		}
	}

	sum = get_sum(transitionProbabilities)
	if !equalFloat(sum, 1.0, 0.00000001) {
		transitionProbabilities = adjust_tps_over_one(transitionProbabilities)
	}

	// ----------------------- Choose new state ------------------------

	// using  final transition probabilities, assign new state
	// var chosen_tp TransitionProbability
	new_state, chosen_tp := pickStateAndTp(transitionProbabilities, random)

	if new_state.Is_uninitialized_state {
		fmt.Println("cant be assigned an unint state")
	}

	// ---------------- active case finding ---------------------

	// CDPH finds ~10 contacts per active case
	// 25% of them have LTBI
	// and 75% of those are recent transmissions

	if cycle.Id > 1 && chain.Id == TB_CHAIN_ID {

		number_of_fast_latents_identified_per_active_case := 10.0 * 0.25 * 0.75
		number_of_slow_latents_identified_per_active_case := 10.0 * 0.25 * 0.25

		number_of_active_cases_last_cycle := float64(Query.Total_active_by_cycle[cycle.Id-1])

		total_fast_latents_identified := number_of_fast_latents_identified_per_active_case * number_of_active_cases_last_cycle
		total_slow_latents_identified := number_of_slow_latents_identified_per_active_case * number_of_active_cases_last_cycle

		chance_fast_latent := total_fast_latents_identified / float64(Query.State_populations_by_cycle[cycle.Id-1][FAST_LATENT_ID])
		chance_slow_latent := total_slow_latents_identified / float64(Query.State_populations_by_cycle[cycle.Id-1][SLOW_LATENT_ID])

		//// grab uninfected

		if uint(currentStateInThisChain.Id) == SLOW_LATENT_ID {
			// assume CDPH uses testing group Id of 0th intervention
			if random < chance_slow_latent {
				new_state = Query.getStateByName(Inputs.Interventions[0].Testing_groups[1].Test_choice_pos)
				Inputs.People[person.Id].TestingGroupId = 1
				TestedThroughActiveCaseFinding += 1
			}

		}
		if uint(currentStateInThisChain.Id) == FAST_LATENT_ID {
			// assume CDPH uses testing group Id of 0th intervention
			if random < chance_fast_latent {
				new_state = Query.getStateByName(Inputs.Interventions[0].Testing_groups[1].Test_choice_pos)
				Inputs.People[person.Id].TestingGroupId = 1
				TestedThroughActiveCaseFinding += 1
			}
		}
	}

	// --------- age -------------

	if chain.Id == AGE_CHAIN_ID {

		//ageChain := chain
		ageState := new_state
		ageStateName := ageState.Name
		if !ageState.Is_death_state {
			//fmt.Println(ageStateName)
			//low := Query.Low_from_age_group[ageStateName]
			high := Query.High_from_age_group[ageStateName]

			if person.Age > float64(high) {
				// too old, need to move them to next age grouping
				// TODO not the best way to do this
				currentAgeStateId := ageState.Id
				newAgeStateId := currentAgeStateId + 1
				new_state = Inputs.States[newAgeStateId]
			}
		}

	}

	// ---------- lenght of time in US ------------

	if chain.Id == LEN_TIME_CHAIN_ID {

		lotState := new_state
		lotStateName := lotState.Name
		if lotStateName == "Less than one year" && person.YearsInUs > 1 {
			new_state = Query.getStateByName("Between one and 5 years")
			// fmt.Println("moved someone with ", person.YearsInUs, "into new category")
		}
		if lotStateName == "Between one and 5 years" && person.YearsInUs > 5 {
			new_state = Query.getStateByName("5 or more years")
			// fmt.Println("moved someone with ", person.YearsInUs, "into new category")
		}

	}

	// ---------- adjust months since TB infection ------------

	if chain.Id == TB_CHAIN_ID {

		tbState := new_state
		tbStateName := tbState.Name

		// intitialization of fast latents
		if tbStateName == "Fast latent" && isInitializationPhase {
			// distribute evenly within first three years
			Inputs.People[person.Id].MonthsSinceTBInfection = math.Floor(rand.Float64() * 36.0)
		}

		// intitialization of slow latents
		if tbStateName == "Slow latent" && isInitializationPhase {
			Inputs.People[person.Id].MonthsSinceTBInfection = 1000
		}

		// intitialization of past-treated
		if tbStateName == "LTBI treated with INH 6m" && isInitializationPhase {
			Inputs.People[person.Id].MonthsSinceTBInfection = 1000
		}

		// if infected, add months to infection
		if tbStateName != "Uninfected TB" &&
			tbStateName != "Uninfected Testing TST" &&
			tbStateName != "Uninfected Testing QFT" &&
			tbStateName != "Uninfected Testing TSPOT" &&
			tbStateName != "Uninfected Testing TST+QFT" &&
			tbStateName != "Uninfected Testing TST+TSPOT" &&
			tbStateName != "FP LBTI 9m INH - Month 1" &&
			tbStateName != "FP LBTI 9m INH - Month 2" &&
			tbStateName != "FP LBTI 9m INH - Month 3" &&
			tbStateName != "FP LBTI 9m INH - Month 4" &&
			tbStateName != "FP LBTI 9m INH - Month 5" &&
			tbStateName != "FP LBTI 9m INH - Month 6" &&
			tbStateName != "FP LBTI 9m INH - Month 7" &&
			tbStateName != "FP LBTI 9m INH - Month 8" &&
			tbStateName != "FP LBTI 9m INH - Month 9" &&
			tbStateName != "FP LTBI 6m INH - Month 1" &&
			tbStateName != "FP LTBI 6m INH - Month 2" &&
			tbStateName != "FP LTBI 6m INH - Month 3" &&
			tbStateName != "FP LTBI 6m INH - Month 4" &&
			tbStateName != "FP LTBI 6m INH - Month 5" &&
			tbStateName != "FP LTBI 6m INH - Month 6" &&
			tbStateName != "FP LTBI RIF - Month 1" &&
			tbStateName != "FP LTBI RIF - Month 2" &&
			tbStateName != "FP LTBI RIF - Month 3" &&
			tbStateName != "FP LTBI RIF - Month 4" &&
			tbStateName != "FP LTBI RTP - Month 1" &&
			tbStateName != "FP LTBI RTP - Month 2" &&
			tbStateName != "FP LTBI RTP - Month 3" &&
			tbStateName != "Death" {
			Inputs.People[person.Id].MonthsSinceTBInfection = Inputs.People[person.Id].MonthsSinceTBInfection + 1
		}
		// reset for self-cures
		if tbStateName == "Uninfected TB" {
			Inputs.People[person.Id].MonthsSinceTBInfection = 0
		}
		// move anyone from fast latent with > 35 months to slow latent
		//technically shouldn't do anything - just for graphing. also not 100% true since people
		// in treatment may still technically be "fast latent"
		if tbStateName == "Fast latent" && person.MonthsSinceTBInfection > 35 {
			new_state = Query.getStateByName("Slow latent")
		}

		if tbStateName == "Slow latent" {
			Inputs.People[person.Id].MonthsSinceTBInfection = 1000
		}

	}

	// ----------- life expectancy ------------

	ageStateName := Inputs.States[Query.Master_record_current_cycle_by_person_and_chain[person.Id][AGE_CHAIN_ID].State_id].Name
	sexStateName := Inputs.States[Query.Master_record_current_cycle_by_person_and_chain[person.Id][SEX_CHAIN_ID].State_id].Name

	// in months
	lifeExpectancy := Query.Life_expectancy_by_sex_and_age[sexStateName][ageStateName]

	// adust based risk factor morbidity
	if hivStateId == INFECTEDHIVNOART_STATE_ID {
		lifeExpectancy = lifeExpectancy * 0.530542013
	}
	if hivStateId == INFECTEDHIVART_STATE_ID {
		lifeExpectancy = lifeExpectancy * 0.530542013
	}
	if diabetesStateId == DIABETES_STATE_ID {
		lifeExpectancy = lifeExpectancy * 0.674678474
	}
	if homeslessnessStateId == HOMELESS_STATE_ID {
		lifeExpectancy = lifeExpectancy * 0.602564103
	}
	if esrdStateId == ESRD_STATE_ID {
		lifeExpectancy = lifeExpectancy * 0.196463654
	}
	if tnfStateId == TNFALPHA_STATE_ID {
		lifeExpectancy = lifeExpectancy * 0.884701373
	}
	if smokerStateId == SMOKER_STATE_ID {
		lifeExpectancy = lifeExpectancy * 0.70459984
	}
	if transplantsStateId == TRANSPLANTPATIENT_STATE_ID {
		lifeExpectancy = lifeExpectancy * 0.297880466
	}

	// ---------- medical risk factor --------------- this has to run last!!

	if chain.Name == "Medical risk factor" {

		if currentStateInThisChain.Is_death_state { // can't bring them back to life!
			new_state = currentStateInThisChain
		} else {
			hasRiskFactorState := Query.getStateByName("Medical risk factor")
			hasNoRiskFactorState := Query.getStateByName("No medical risk factor")

			hasRiskFactor := false
			for c := 0; c < len(Inputs.Chains); c++ {
				stateId := Query.Master_record_current_cycle_by_person_and_chain[person.Id][c].State_id
				state := Inputs.States[stateId]
				if state.Is_medical_risk_factor {
					//fmt.Println("Medical risk factor: ", state.Name)
					hasRiskFactor = true
				}
			}

			if hasRiskFactor {
				new_state = hasRiskFactorState
			} else {
				new_state = hasNoRiskFactorState
			}

		}

	}

	// ------ costs ---------

	mr = &Query.Master_record_next_cycle_by_person_and_chain[person.Id][chain.Id]

	//Cost calculations
	discountValue := math.Pow(1.0-(Discount.Value/12.0), float64(cycle.Id-181))
	costs := Query.Cost_by_state_id[new_state.Id] * discountValue
	NegQaly := 0.0

	// ------ health metrics ---------

	if cycle.Id > 0 {
		// active TB cases incure negative qalys (I know really should be dalys,
		// but its domestic so working with qalys. just easier to record negative
		// than positive)
		// the only negative health impact we care about is cases of active TB
		// we assume same QALY loss for each active case, as a simplication
		if new_state.Id == ACTIVE_UNTREATED_ID &&
			currentStateInThisChain.Id != ACTIVE_UNTREATED_ID &&
			currentStateInThisChain.Id != ACTIVE_TREATED_M1_ID &&
			currentStateInThisChain.Id != ACTIVE_TREATED_M2_ID &&
			currentStateInThisChain.Id != ACTIVE_TREATED_M3_ID &&
			currentStateInThisChain.Id != ACTIVE_TREATED_M4_ID &&
			currentStateInThisChain.Id != ACTIVE_TREATED_M5_ID &&
			currentStateInThisChain.Id != ACTIVE_TREATED_M6_ID &&
			currentStateInThisChain.Id != DEFAULT_ID {
			//a new active case
			NegQaly = QalysGainedAvertingOneCaseOfActiveTb.Value * discountValue
		}
		// mortality
		justDied := new_state.Is_death_state && !currentStateInThisChain.Is_death_state
		// Sync deaths with other chains
		if justDied {
			// Sync deaths. Put person in "other death"
			for _, sub_chain := range Inputs.Chains {
				//skip current chain because should show disease-specific death
				if sub_chain.Id != chain.Id {
					otherDeathState := getDeathStateByChain(sub_chain)
					// For the next cycle - in case this chain has already
					// passed and they were assigned a new state
					mr = &Query.Master_record_next_cycle_by_person_and_chain[person.Id][sub_chain.Id]
					mr.State_id = otherDeathState.Id
					//once they've been assigned a death state, need to clear
					// their other information (in case another chain filled in
					// the data for the state they would have done to. But they've
					// died, so we need to clear the Ylls, Ylds, and Costs
					mr.Ylds = 0
					mr.Ylls = 0
					mr.Costs = 0
					mr.Has_entered_simulation = true
					mr.State_name = "Other death"
				}
			}
		}
	}
	// // check to make sure they are not mis-assigned
	// if new_state.Is_death_state && !currentStateInThisChain.Is_death_state {
	// 	fmt.Println("Should not be assigned other death here")
	// 	os.Exit(1)
	// }

	if new_state.Id < 1 {
		fmt.Println("No new state!")
		os.Exit(1)
	}

	// Store in two places, the master record and ...
	// mrId = Query.Master_record_id_by_cycle_and_person_and_chain[cycleIdToSave][person.Id][chain.Id]

	if isInitializationPhase {
		// this function, RunCyclePersonChain, is used by both the initialization phase
		// and throughout the model running. If it is used for the initialzaiton phase,
		// you save the new state in the current cycle ( zero for the beginning pop),
		// otherwise, it needs to be saved in the next future cycle.
		mr = &Query.Master_record_current_cycle_by_person_and_chain[person.Id][chain.Id]
	} else {
		mr = &Query.Master_record_next_cycle_by_person_and_chain[person.Id][chain.Id]
		Query.State_populations_by_cycle[cycle.Id][new_state.Id] += 1
	}

	mr.State_id = new_state.Id
	mr.RiskOfProgression = riskOfProgression
	mr.Has_entered_simulation = true
	mr.Is_tracked = chosen_tp.Is_tracked
	mr.Entered_from_state = currentStateInThisChain.Id
	mr.Months_life_remaining = lifeExpectancy
	mr.Costs = costs
	mr.NegQaly = NegQaly
	mr.Age = person.Age
	mr.Months_since_TB_infection = uint(person.MonthsSinceTBInfection)
	mr.Risk_of_infection = riskOfInfection

	// ... the state holder.. and
	// Query.State_id_by_cycle_and_person_and_chain[cycleIdToSave][person.Id][chain.Id] = new_state.Id

	// state population tracker
	var check_new_state_id uint
	if isInitializationPhase {
		check_new_state_id = Query.Master_record_current_cycle_by_person_and_chain[person.Id][chain.Id].State_id
	} else {
		check_new_state_id = Query.Master_record_next_cycle_by_person_and_chain[person.Id][chain.Id].State_id

	}

	if check_new_state_id != new_state.Id {
		fmt.Println("Was not correctly assigned... bug")
		os.Exit(1)
	}

}

func adjust_recursive_tp(transitionProbabilities []TransitionProbability) []TransitionProbability {
	sum := 0.0
	var recursiveTp *TransitionProbability
	for i, tp := range transitionProbabilities {
		if tp.From_state_id == tp.To_state_id {
			recursiveTp = &transitionProbabilities[i]
		} else {
			sum = sum + tp.Tp_base
		}
	}
	recursiveTp.Tp_base = 1 - sum
	return transitionProbabilities
}

func getReducedChains() []Chain {

	var reducedChains []Chain

	chain_names := []string{"Diabetes",
		"Homeless",
		"TB disease and treatment",
		"HIV risk groups",
		"ESRD",
		"TNF-alpha",
		"HIV",
		"Alcohol",
		"Close contacts",
		"Smoking",
		"Natural death",
		"Transplants",
		"Medical risk factor"} //medical risk factor needs to be last

	// chainNamesAlreadyInitialized := []string{"Sex", "Race", "Age grouping", "Citizen", "Length of time in US"}
	for _, chain_name := range chain_names {
		chain := Query.getChainByName(chain_name)
		reducedChains = append(reducedChains, chain)
	}

	//fmt.Println(reducedChains)
	return reducedChains
}

func initializeOnePerson(cycle Cycle, person Person, generalChan chan uint, mutex *sync.Mutex) {

	// remove the chains that were initialized in create people
	reducedChains := ReducedChains

	// sortedChains := getChainsSortedByInitOrder()
	//shuffled := shuffle(Inputs.Chains, mutex, person.Id)
	for _, chain := range reducedChains { // foreach chain

		if person.Id == 1 {
			//fmt.Println(chain.Name)
		}
		// cannot be made concurrent, because if they die in one chain
		runCyclePersonChain(cycle.Id, chain.Id, person.Id, true)
	}
	generalChan <- 1
}

func getChainsSortedByInitOrder() []Chain {
	var orderedChains []Chain
	for _, chain := range Inputs.Chains {
		if chain.Name == "Race" || chain.Name == "Sex" || chain.Name == "Age grouping" {
			orderedChains = append(orderedChains, chain)
		}
	}
	for _, chain := range Inputs.Chains {
		if chain.Name != "Race" || chain.Name != "Sex" || chain.Name != "Age grouping" {
			orderedChains = append(orderedChains, chain)
		}
	}
	return orderedChains
}

func runOneCycleForOnePerson(cycleId uint, personId uint, generalChan chan uint) {
	// TODO: Removed shuffle
	for chainId := 0; chainId < 19; chainId++ {
		// cannot be made concurrent, because if they die in one chain
		runCyclePersonChain(cycleId, uint(chainId), personId, false)
	}
	generalChan <- 1
}

//////////////////////////////// OUTPUTS
