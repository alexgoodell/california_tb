package main

////////////////////// ---------- IO -------------- //////////////////////
import (
	"encoding/csv"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"reflect"

	"gopkg.in/yaml.v2"

	"github.com/jinzhu/gorm"
)

func check(e error) {
	if e != nil {
		panic(e)
	}
}

func initializeInputs(NumberOfCycles uint) {

	db, err := gorm.Open("sqlite3", DATABASE_PATH)

	//remove rows from previous simulations
	db.Exec("DELETE FROM outputs_by_cycle_state")

	if err != nil {
		fmt.Println("error connecting to database")
		pause()
		pause()
		pause()
		pause()
		initializeInputs(NumberOfCycles)
	}

	var tps_by_intervention []Transition_probability_by_intervention
	db.Find(&tps_by_intervention)
	Inputs.TransitionProbabiliesByIntervention = tps_by_intervention

	// ####################### Synchronizations #######################

	var synchronizations []Synchronization
	db.Find(&synchronizations)
	Inputs.Synchronizations = synchronizations

	// ####################### Stratum types #######################

	var stratum_types []Stratum_type
	db.Find(&stratum_types)
	Inputs.StratumTypes = stratum_types

	// ####################### strata #######################

	var strata []Stratum
	db.Find(&strata)
	Inputs.Strata = strata

	// ####################### stratum_type_contents #######################

	var stratum_type_contents []Stratum_type_content
	db.Find(&stratum_type_contents)
	Inputs.StratumTypeContents = stratum_type_contents

	// ####################### stratum_contents #######################

	var stratum_contents []Stratum_content
	db.Find(&stratum_contents)
	Inputs.StratumContents = stratum_contents

	// ####################### trans_prob_by_stratum #######################

	var trans_prob_by_stratum []Transition_probability_by_stratum
	db.Find(&trans_prob_by_stratum)
	Inputs.TransitionProbabilitiesByStratum = trans_prob_by_stratum

	// ####################### vars_by_stratum #######################

	var vars_by_stratum []Variable_by_stratum
	db.Find(&vars_by_stratum)
	Inputs.VariablesByStratum = vars_by_stratum

	// ####################### Variables #######################

	var variables []Variable
	db.Find(&variables)
	Inputs.Variables = variables
	//fmt.Println("complete")

	// ####################### Chains #######################

	var chains []Chain
	db.Find(&chains)
	Inputs.Chains = chains
	//fmt.Println("complete")

	// ####################### States #######################

	var states []State
	db.Find(&states)
	Inputs.States = states

	// ####################### Transition Probabilities #######################

	var tps []TransitionProbability
	db.Find(&tps)
	//fmt.Println(tps)
	Inputs.TransitionProbabilities = tps
	// fmt.Println(tps[4])
	// fmt.Println(tps[4].Tp_base)
	// fmt.Println(tps[4].Tp_base * 1.0)
	// os.Exit(1)
	fmt.Println(" initialize inputs TP 4: ", Inputs.TransitionProbabilities[4].Tp_base)

	// ####################### Interactions #######################

	var interactions []Interaction
	db.Find(&interactions)
	Inputs.Interactions = interactions

	// ####################### Cycles #######################

	var cycles []Cycle

	if RunType == "single" {
		db.Find(&cycles)
		fmt.Println("Attempting to import ", NumberOfCycles, " cycles")
		fmt.Println("Found ", len(cycles), " cycles in db")
		Inputs.Cycles = cycles[:NumberOfCycles]
		fmt.Println("Imported ", len(Inputs.Cycles), " cycles")
	}

	if RunType == "calib" || RunType == "psa" || RunType == "dsa" {
		data, err := ioutil.ReadFile("raw-data-files/calib_cycles.yaml")
		check(err)

		err = yaml.Unmarshal([]byte(data), &cycles)
		if err != nil {
			log.Fatalf("error: %v", err)
		}

		if int(NumberOfCycles) > len(cycles) {
			fmt.Println("Cannot run that many cycles")
			os.Exit(1)
		} else {
			Inputs.Cycles = cycles[:NumberOfCycles]
		}

	}

	// ####################### Costs #######################

	var costs []Cost
	db.Find(&costs)
	Inputs.Costs = costs

	// ####################### Disability Weights #######################

	var dws []DisabilityWeight
	db.Find(&dws)
	Inputs.DisabilityWeights = dws

	// ####################### BaseInitLines #######################

	//fmt.Println("importing from baseinitlines")
	var baseInitLines []BaseInitLine
	db.Find(&baseInitLines)
	Inputs.BaseInitLines = baseInitLines

	// ####################### Interventions #######################

	// read from a yaml file

	data, err := ioutil.ReadFile("go/scenarios/" + SimName + "-config.yaml")
	check(err)

	err = yaml.Unmarshal([]byte(data), &Inputs.Interventions)
	if err != nil {
		log.Fatalf("error: %v", err)
	}

	fmt.Println(Inputs.Interventions)

}

func addThisCycleToOutputs(cycleId uint) {

	slowLatentStateId := SLOW_LATENT_ID
	// we assume some portion of population is treated already with 6m INH
	latentTreatedStateId := Query.getStateByName("LTBI treated with INH 6m").Id
	fastLatentStateId := FAST_LATENT_ID
	activeStateId := ACTIVE_UNTREATED_ID
	tbChainId := TB_CHAIN_ID
	lenInUsChain := LEN_TIME_CHAIN_ID
	usBornId := Query.getStateByName("Not Foreign-born").Id

	var masterRecordsToUse [][]MasterRecord
	masterRecordsToUse = Query.Master_record_next_cycle_by_person_and_chain

	for p := 0; uint(p) < NumberOfPeople; p++ {
		for ch := 0; ch < len(Inputs.Chains); ch++ {

			masterRecord := masterRecordsToUse[p][ch]
			if masterRecord.Has_entered_simulation {

				//masterRecordLastCycle := Query.Master_record_current_cycle_by_person_and_chain[p][ch]

				outputCSId := Query.Outputs_id_by_cycle_and_state[cycleId][masterRecord.State_id]
				outputCS := &Outputs.OutputsByCycleStateFull[outputCSId]
				if outputCS.Cycle_id != cycleId || outputCS.State_id != masterRecord.State_id {
					fmt.Println("problem formating ouput by state cycle")
					os.Exit(1)
				}

				tbMasterRecord := masterRecordsToUse[masterRecord.Person_id][tbChainId]

				tbStateId := tbMasterRecord.State_id
				lenInUsStateId := masterRecordsToUse[masterRecord.Person_id][lenInUsChain].State_id
				isHcw := Inputs.People[masterRecord.Person_id].IsHcw
				isFb := !(lenInUsStateId == usBornId)
				wasTransmissionInUs := 0

				// risk of progression

				// if  tbMasterRecord.RiskOfProgression != 0 {
				// 	fmt.Println(cycleId, " : ", tbMasterRecord.RiskOfProgression)
				// }

				if isFb {
					outputCS.Risk_of_prog_fb += tbMasterRecord.RiskOfProgression
				} else {
					outputCS.Risk_of_prog_us += tbMasterRecord.RiskOfProgression
				}

				switch tbStateId {

				case slowLatentStateId:

					if isFb {
						outputCS.Slow_latents_fb += 1
					} else {
						outputCS.Slow_latents_us += 1
					}

				// count them as latent (used to display initialization of latents in calibration)
				case latentTreatedStateId:

					if isFb {
						outputCS.Slow_latents_fb += 1
					} else {
						outputCS.Slow_latents_us += 1
					}

				case fastLatentStateId:

					lastTbState := Query.Master_record_current_cycle_by_person_and_chain[masterRecord.Person_id][tbChainId].State_id
					if Inputs.States[lastTbState].Id == UNINF_ID {
						wasTransmissionInUs = 1
					}

					if isFb {
						outputCS.Fast_latents_fb += 1
					} else {
						outputCS.Fast_latents_us += 1
					}

				case activeStateId:
					// if cycle is 0, assume TB case came from initialization
					lastTbState := uint(0)
					// else, look for where it came from
					// if cycleId != 0 {
					lastTbState = Query.Master_record_current_cycle_by_person_and_chain[masterRecord.Person_id][tbChainId].State_id
					// }
					if lastTbState != activeStateId {
						if isFb {
							outputCS.Active_cases_fb += 1
						} else {
							outputCS.Active_cases_us += 1
						}
					}

				}

				if isFb {
					outputCS.Population_fb += 1
				} else {
					outputCS.Population_us += 1
				}

				if isHcw {
					outputCS.HCW_in_state += 1
				}

				if isFb {
					outputCS.Months_life_remaining_fb += masterRecord.Months_life_remaining
				} else {
					outputCS.Months_life_remaining_us += masterRecord.Months_life_remaining
				}

				if isFb {
					outputCS.Risk_of_infection_fb += masterRecord.Risk_of_infection
				} else {
					outputCS.Risk_of_infection_us += masterRecord.Risk_of_infection
				}

				// if infected
				if Inputs.States[tbStateId].Name != "Uninfected TB" &&
					Inputs.States[tbStateId].Name != "Unintialized" &&
					Inputs.States[tbStateId].Name != "Uninfected Testing TST" &&
					Inputs.States[tbStateId].Name != "Uninfected Testing QFT" &&
					Inputs.States[tbStateId].Name != "Uninfected Testing TSPOT" &&
					Inputs.States[tbStateId].Name != "Uninfected Testing TST+QFT" &&
					Inputs.States[tbStateId].Name != "Uninfected Testing TST+TSPOT" &&
					Inputs.States[tbStateId].Name != "FP LBTI 9m INH - Month 1" &&
					Inputs.States[tbStateId].Name != "FP LBTI 9m INH - Month 2" &&
					Inputs.States[tbStateId].Name != "FP LBTI 9m INH - Month 3" &&
					Inputs.States[tbStateId].Name != "FP LBTI 9m INH - Month 4" &&
					Inputs.States[tbStateId].Name != "FP LBTI 9m INH - Month 5" &&
					Inputs.States[tbStateId].Name != "FP LBTI 9m INH - Month 6" &&
					Inputs.States[tbStateId].Name != "FP LBTI 9m INH - Month 7" &&
					Inputs.States[tbStateId].Name != "FP LBTI 9m INH - Month 8" &&
					Inputs.States[tbStateId].Name != "FP LBTI 9m INH - Month 9" &&
					Inputs.States[tbStateId].Name != "FP LTBI 6m INH - Month 1" &&
					Inputs.States[tbStateId].Name != "FP LTBI 6m INH - Month 2" &&
					Inputs.States[tbStateId].Name != "FP LTBI 6m INH - Month 3" &&
					Inputs.States[tbStateId].Name != "FP LTBI 6m INH - Month 4" &&
					Inputs.States[tbStateId].Name != "FP LTBI 6m INH - Month 5" &&
					Inputs.States[tbStateId].Name != "FP LTBI 6m INH - Month 6" &&
					Inputs.States[tbStateId].Name != "FP LTBI RIF - Month 1" &&
					Inputs.States[tbStateId].Name != "FP LTBI RIF - Month 2" &&
					Inputs.States[tbStateId].Name != "FP LTBI RIF - Month 3" &&
					Inputs.States[tbStateId].Name != "FP LTBI RIF - Month 4" &&
					Inputs.States[tbStateId].Name != "FP LTBI RTP - Month 1" &&
					Inputs.States[tbStateId].Name != "FP LTBI RTP - Month 2" &&
					Inputs.States[tbStateId].Name != "FP LTBI RTP - Month 3" &&
					Inputs.States[tbStateId].Name != "Death" {

					if masterRecord.Months_since_TB_infection < 36 {
						if isFb {
							outputCS.Recent_transmission_fb += 1
							outputCS.Recent_transmission_fb_rop += tbMasterRecord.RiskOfProgression
						} else {
							outputCS.Recent_transmission_us += 1
							outputCS.Recent_transmission_us_rop += tbMasterRecord.RiskOfProgression
						}
					}

				}

				outputCS.Transmission_within_us += uint(wasTransmissionInUs)
				outputCS.Chain_id = masterRecord.Chain_id
				outputCS.Costs += masterRecord.Costs
				outputCS.Ylds += masterRecord.Ylds
				outputCS.Ylls += masterRecord.Ylls
				outputCS.Dalys += masterRecord.Ylds + masterRecord.Ylls
				outputCS.Age += masterRecord.Age
				outputCS.Population += 1

			}

		}
	}

}

//////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////

func formatOutputs() {

	// slowLatentStateId := Query.getStateByName("Slow latent").Id
	// fastLatentStateId := Query.getStateByName("Fast latent").Id
	// activeStateId := Query.getStateByName("Active - untreated").Id
	// tbChainId := Query.getChainByName("TB disease and treatment").Id
	// lenInUsChain := Query.getChainByName("Length of time in US").Id
	// usBornId := Query.getStateByName("Not Foreign-born").Id

	// // var reducedMasterRecords []MasterRecord

	// for _, masterRecord := range Inputs.MasterRecords {

	// 	outputCSId := Query.Outputs_id_by_cycle_and_state[masterRecord.Cycle_id][masterRecord.State_id]
	// 	outputCS := &Outputs.OutputsByCycleStateFull[outputCSId]
	// 	if outputCS.Cycle_id != masterRecord.Cycle_id || outputCS.State_id != masterRecord.State_id {
	// 		fmt.Println("problem formating ouput by state cycle")
	// 		os.Exit(1)
	// 	}

	// 	tbMasterRecordId := Query.Master_record_id_by_cycle_and_person_and_chain[masterRecord.Cycle_id][masterRecord.Person_id][tbChainId]
	// 	tbMasterRecord := Inputs.MasterRecords[tbMasterRecordId]

	// 	tbStateId := Query.State_id_by_cycle_and_person_and_chain[masterRecord.Cycle_id][masterRecord.Person_id][tbChainId]
	// 	lenInUsStateId := Query.State_id_by_cycle_and_person_and_chain[masterRecord.Cycle_id][masterRecord.Person_id][lenInUsChain]
	// 	isFb := !(lenInUsStateId == usBornId)

	// 	// risk of progression

	// 	if isFb {
	// 		outputCS.Risk_of_prog_fb += tbMasterRecord.RiskOfProgression
	// 	} else {
	// 		outputCS.Risk_of_prog_us += tbMasterRecord.RiskOfProgression
	// 	}

	// 	switch tbStateId {

	// 	case slowLatentStateId:

	// 		if isFb {
	// 			outputCS.Slow_latents_fb += 1
	// 		} else {
	// 			outputCS.Slow_latents_us += 1
	// 		}

	// 	case fastLatentStateId:

	// 		if isFb {
	// 			outputCS.Fast_latents_fb += 1
	// 		} else {
	// 			outputCS.Fast_latents_us += 1
	// 		}

	// 	case activeStateId:
	// 		// if cycle is 0, assume TB case came from initialization
	// 		lastTbState := 0
	// 		// else, look for where it came from
	// 		if masterRecord.Cycle_id != 0 {
	// 			lastTbState = Query.State_id_by_cycle_and_person_and_chain[masterRecord.Cycle_id-1][masterRecord.Person_id][tbChainId]
	// 		}
	// 		if lastTbState != activeStateId {
	// 			if isFb {
	// 				outputCS.Active_cases_fb += 1
	// 			} else {
	// 				outputCS.Active_cases_us += 1
	// 			}
	// 		}

	// 	}

	// 	if isFb {
	// 		outputCS.Population_fb += 1
	// 	} else {
	// 		outputCS.Population_us += 1
	// 	}

	// 	outputCS.Chain_id = masterRecord.Chain_id
	// 	outputCS.Costs += masterRecord.Costs
	// 	outputCS.Ylds += masterRecord.Ylds
	// 	outputCS.Ylls += masterRecord.Ylls
	// 	outputCS.Dalys += masterRecord.Ylds + masterRecord.Ylls
	// 	outputCS.Population += 1

	// }

	// for i := 0; i < len(Outputs.OutputsByCycleStateFull); i++ {
	// 	Outputs.OutputsByCycleStateFull[i].Iteration_num = IterationNum
	// 	Outputs.OutputsByCycleStateFull[i].Intervention_id = InterventionId
	// }

	// overwrite master record
	// Inputs.MasterRecords = reducedMasterRecords

	// 	/// per cycle outputs

	// 	outputByCycle := &Outputs.OutputsByCycle[masterRecord.Cycle_id]
	// 	outputByCycle.Cycle_id = masterRecord.Cycle_id
	// 	evMapper := make(map[string]*int)
	// 	evMapper["T2DM"] = &outputByCycle.T2DM_diagnosis_event
	// 	evMapper["T2DM death"] = &outputByCycle.T2DM_death_event
	// 	evMapper["CHD"] = &outputByCycle.CHD_diagnosis_event
	// 	evMapper["CHD death"] = &outputByCycle.CHD_death_event
	// 	evMapper["HCC"] = &outputByCycle.HCC_diagnosis_event
	// 	evMapper["HCC death"] = &outputByCycle.HCC_death_event

	// 	eventStateNames := []string{"T2DM", "T2DM death", "CHD", "CHD death", "HCC"}
	// 	for _, eventStateName := range eventStateNames {
	// 		eventStateId := Query.getStateByName(eventStateName).Id

	// 		oldState := Inputs.States[oldStateId]

	// 		// Find if they just transfered to the state of interest
	// 		if currentStateId == eventStateId && oldStateId != eventStateId && !oldState.Is_uninitialized_2_state {

	// 			*evMapper[eventStateName] += 1
	// 		}
	// 		//HCC is handled differently, because there is no "HCC death" state. So,
	// 		// we are looking for people who's last state was HCC and are now in the
	// 		// "liver death" group
	// 		hccStateId := Query.getStateByName("HCC").Id
	// 		liverDeathStateId := Query.getStateByName("Liver death").Id
	// 		if currentStateId == liverDeathStateId && oldStateId == hccStateId {
	// 			*evMapper["HCC death"] += 1
	// 		}
	// 	}

	// }

	// Outputs.OutputsByCycleStatePsa = make([]OutputByCycleState, 0, 0)

	// for _, outputCS := range Outputs.OutputsByCycleStateFull {
	// 	stateNamesForPSA := []string{
	// 		"Steatosis",
	// 		"NASH", "Cirrhosis",
	// 		"HCC", "Liver death",
	// 		"Natural death", "CHD",
	// 		"CHD death", "T2DM", "T2DM death",
	// 		"Overweight", "Obese"}

	// 	for _, stateName := range stateNamesForPSA {
	// 		stateId := Query.getStateByName(stateName).Id
	// 		if stateId == outputCS.State_id {
	// 			Outputs.OutputsByCycleStatePsa = append(Outputs.OutputsByCycleStatePsa, outputCS)
	// 		}
	// 	}
	// }

}

func removeUnborns() {

	//print("Removing unborn ... ")
	i := 0
	masterRecordsToReturn := make([]MasterRecord, len(Inputs.MasterRecords), len(Inputs.MasterRecords))
	for p, _ := range Inputs.MasterRecords {
		if Inputs.MasterRecords[p].Has_entered_simulation == true {
			masterRecordsToReturn[i] = Inputs.MasterRecords[p]
			i++
		}
	}
	Inputs.MasterRecords = masterRecordsToReturn[:i]
	//printComplete()
}

// Exports sets of data to CSVs. I particular, it will print any array of structs
// and automatically uses the struct field names as headers! wow.
// It takes a filename, as well one copy of the struct, and the array of structs
// itself.
func toCsv(filename string, record interface{}, records interface{}) error {
	fmt.Println("Beginning export to ", filename)
	//create or open file
	os.Create(filename)
	file, err := os.OpenFile(filename, os.O_RDWR|os.O_APPEND|os.O_CREATE, 0666)
	if err != nil {
		panic(err)
	}
	defer file.Close()
	// new Csv wriier
	writer := csv.NewWriter(file)
	// use the single record to determine the fields of the struct
	val := reflect.Indirect(reflect.ValueOf(record))
	numberOfFields := val.Type().NumField()
	var fieldNames []string
	for i := 0; i < numberOfFields; i++ {
		fieldNames = append(fieldNames, val.Type().Field(i).Name)
	}
	// print field names of struct
	err = writer.Write(fieldNames)
	// print the values from the array of structs
	val2 := reflect.ValueOf(records)
	for i := 0; i < val2.Len(); i++ {
		var line []string
		for p := 0; p < numberOfFields; p++ {
			//convert interface to string
			line = append(line, fmt.Sprintf("%v", val2.Index(i).Field(p).Interface()))
		}
		err = writer.Write(line)
	}
	if err != nil {
		fmt.Println("error")
		os.Exit(1)
	}
	//fmt.Println("Exported to ", filename)
	writer.Flush()
	return err
}
