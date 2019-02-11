package main

import (
	"fmt"
	_ "net/http/pprof"
	"os"

	"github.com/codegangsta/cli"
)

func main() {

	// go func() {
	// 	log.Println(http.ListenAndServe("localhost:6060", nil))
	// }()

	// size := "m"
	// NumberOfCycles := 16
	// NumberOfIterations = 1
	// SimName = "testr"
	// startRunWithSingle(size, NumberOfCycles, NumberOfIterations, SimName)

	app := cli.NewApp()
	app.Name = "LIMCAT"
	app.Usage = "limcat help for help"
	app.Version = "dev-0.1"

	// TODO_LATER: Build flag system out
	app.Flags = []cli.Flag{
		cli.StringFlag{
			Name:  "size",
			Value: "s",
			Usage: "s m or l",
		},
		cli.StringFlag{
			Name:  "name",
			Value: "untitled",
			Usage: "name of this simulation",
		},
		cli.StringFlag{
			Name:  "run_name",
			Value: "code",
			Usage: "codename of this simulation",
		},
		cli.StringFlag{
			Name:  "run_type",
			Value: "single",
			Usage: "singe, calib, psa, or dsa",
		},
		cli.IntFlag{
			Name:  "cycles",
			Value: 16,
			Usage: "number of cycles",
		},
		cli.IntFlag{
			Name:  "runs",
			Value: 1,
			Usage: "number of runs",
		},
		cli.IntFlag{
			Name:  "psa_runs",
			Value: 1,
			Usage: "number of runs for PSA",
		},
		cli.IntFlag{
			Name:  "closedcohort",
			Value: 0,
			Usage: "closed cohort",
		},
		cli.IntFlag{
			Name:  "adjustment_factor",
			Value: 10000,
			Usage: "determines size of model",
		},
		cli.IntFlag{
			Name:  "disallow_retest",
			Value: 0,
			Usage: "whether retesting allowed",
		},
	}

	app.Action = func(c *cli.Context) {
		fmt.Println("hello!!!")
		size := c.String("size")
		RunType = c.String("run_type")
		adjustmentFactor := float64(c.Int("adjustment_factor"))
		fmt.Println("size = ", size)
		NumberOfCycles := uint(c.Int("cycles"))
		NumberOfIterations = uint(c.Int("runs"))
		IsClosedCohort = uint(c.Int("closedcohort"))
		SimName = c.String("name")
		RunName = c.String("run_name")
		PsaNumberOfRuns = c.Int("psa_runs")
		Disallow_retest = c.Int("disallow_retest")

		if RunType == "single" {
			beginAnalysis(size, NumberOfCycles, NumberOfIterations, SimName, IsClosedCohort, adjustmentFactor)
		}

		if RunType == "calib" {
			beginAnalysis(size, NumberOfCycles, NumberOfIterations, SimName, IsClosedCohort, adjustmentFactor)
			// startRunWithSingle(size, NumberOfCycles, NumberOfIterations, SimName, IsClosedCohort)
		}

		if RunType == "psa" {
			beginAnalysis(size, NumberOfCycles, NumberOfIterations, SimName, IsClosedCohort, adjustmentFactor)
		}

		if RunType == "dsa" {
			beginAnalysis(size, NumberOfCycles, NumberOfIterations, SimName, IsClosedCohort, adjustmentFactor)
		}

	}

	app.Run(os.Args)

}

func startRunWithPsa(size string, NumberOfCycles uint, NumberOfIterations uint, SimName string, IsClosedCohort uint) {

	// SimName = SimName

	// // Hi from LIMCAT
	// show_greeting()

	// printMemoryUse("Before simluation")

	// // print name of sim
	// fmt.Println("Running simulation: ", SimName)

	// fmt.Println("================= PSA ====================== ")

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

	// var adjustmentFactor float64

	// if size == "s" {
	// 	adjustmentFactor = 1000
	// } else if size == "m" {
	// 	adjustmentFactor = 100
	// } else if size == "l" {
	// 	adjustmentFactor = 10
	// }

	// NumberOfPeopleStarting = uint(float64(NumberOfPeopleStartingByYear[2001]) / adjustmentFactor)

	// AdjustedNumberOfPeopleEnteringPerCycleByYear = make(map[int]uint)

	// NumberOfPeopleEntering = 0
	// for i := 0; i < (int(NumberOfCycles) + 1); i++ {
	// 	year := 2001 + int(math.Floor(float64(i)/float64(12)))
	// 	enteringThisCycleUnadj := NumberOfPeopleEnteringByYear[year] / 12
	// 	enteringThisCycleAdj := uint(math.Floor(float64(enteringThisCycleUnadj) / adjustmentFactor))
	// 	AdjustedNumberOfPeopleEnteringPerCycleByYear[year] = enteringThisCycleAdj
	// 	NumberOfPeopleEntering = NumberOfPeopleEntering + enteringThisCycleAdj
	// }

	// if IsClosedCohort == 1 {
	// 	NumberOfPeopleEnteringPerYear = 0
	// }

	// NumberOfPeople = NumberOfPeopleEntering + NumberOfPeopleStarting

	// RunAdjustment = adjustmentFactor

	// // these are the totals for the number of people in the "sample" from the
	// // current cohort and the incoming cohort in IPUMS
	// TotalIpumsNew = int(NumberOfPeopleEnteringByYear[2004])
	// TotalIpumsCurrent = int(NumberOfPeopleStartingByYear[2001])

	// fmt.Println("and ", NumberOfPeopleStarting, "initial individuals")
	// fmt.Println("and ", NumberOfPeopleEntering, "individuals entering")
	// fmt.Println("and ", NumberOfPeople, "total")

	// setEnvironment()

	// initializeInputs(NumberOfCycles)

	// printMemoryUse("After inputs initialization")

	// initializeVariables()
	// calculateVariables()

	// Query.setUp()

	// initializeConstants()

	// printMemoryUse("After query set-up")

	// runInterventions(NumberOfIterations)

	// printMemoryUse("after simulation")

	// // 	mem.Alloc - these are the bytes that were allocated and still in use

	// // mem.TotalAlloc - what we allocated throughout the lifetime

	// // mem.HeapAlloc - what’s being used on the heap right now

	// // mem.HeapSys - this includes what is being used by the heap and what has been reclaimed but not given back out

	// p.Stop()

}

// var VariableCount uint
// var WithinVariableCount uint

func startRunWithDsa() {
	// runType = "dsa"
	// initialize()

	// for i := 0; i < 76; i++ {
	// 	for p := 1; p < 6; p++ {
	// 		VariableCount = i
	// 		WithinVariableCount = p
	// 		initializeInputs(inputsPath)
	// 		Query.setUp()
	// 		runNewDsaValue(i, p)
	// 		runDsa()
	// 		randomLetters = randSeq(10)
	// 		runInterventions()
	// 	}
	// }

	// // create people will generate individuals and add their data to the master
	// // records

	// fmt.Println("Intialization complete, time elapsed:", fmt.Sprint(time.Since(beginTime)))

	// // table tests here
}
