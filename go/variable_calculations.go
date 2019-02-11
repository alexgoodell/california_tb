package main

import (
	"fmt"
	"os"
	"strings"
)

var RecentInfectionAdjustment float64

func calculateVariables() {

	conv := make(map[string]float64)

	RecentInfectionAdjustment = FastLatentProgression.Value / SlowLatentProgression.Value

	// ----------- fasle positives testing

	// conv["Uninfected TB -> Uninfected Testing TST"] = AccessMonthlyProportionOfTrueNegativesThatAreTested.Value
	// conv["Uninfected TB -> Uninfected Testing QFT"] = AccessMonthlyProportionOfTrueNegativesThatAreTested.Value
	// conv["Uninfected TB -> Uninfected Testing TSPOT"] = AccessMonthlyProportionOfTrueNegativesThatAreTested.Value
	// conv["Uninfected TB -> Uninfected Testing TST+QFT"] = AccessMonthlyProportionOfTrueNegativesThatAreTested.Value
	// conv["Uninfected TB -> Uninfected Testing TST+TSPOT"] = AccessMonthlyProportionOfTrueNegativesThatAreTested.Value

	// ----------- false positives enrolling in treatment (current system)

	esrdStateNames := []string{"ESRD", "No ESRD"}
	hivStateNames := []string{"Uninfected HIV", "Infected HIV, no ART", "Infected HIV, ART"}
	testingInfectedStateNames := []string{"Infected Testing TST", "Infected Testing QFT", "Infected Testing TSPOT", "Infected Testing TST+QFT", "Infected Testing TST+TSPOT"}
	testingUninfectedStateNames := []string{"Uninfected Testing TST", "Uninfected Testing QFT", "Uninfected Testing TSPOT", "Uninfected Testing TST+QFT", "Uninfected Testing TST+TSPOT"}

	lotStateNames := []string{"Not Foreign-born", "Less than one year", "Between one and 5 years", "5 or more years"}

	treatmentInfectedStateNames := []string{"LBTI 9m INH - Month 1", "LTBI 6m INH - Month 1", "LTBI RIF - Month 1", "LTBI RTP - Month 1"}
	treatmentUninfectedStateNames := []string{"FP LBTI 9m INH - Month 1", "FP LTBI 6m INH - Month 1", "FP LTBI RIF - Month 1", "FP LTBI RTP - Month 1"}

	for _, esrdStateName := range esrdStateNames {

		for _, lotStateName := range lotStateNames {
			for _, hivStateName := range hivStateNames {

				// true positives
				for _, treatmentInfectedStateName := range treatmentInfectedStateNames {
					for _, testingInfectedStateName := range testingInfectedStateNames {

						// esrdState := Query.getStateByName(esrdStateName)
						// dmState := Query.getStateByName(dmStateName)
						// lotState := Query.getStateByName(lotStateName)
						treatmentInfectedState := Query.getStateByName(treatmentInfectedStateName)
						testingInfectedState := Query.getStateByName(testingInfectedStateName)

						tpId := Query.Tp_id_by_from_state_and_to_state[testingInfectedState.Id][treatmentInfectedState.Id]

						if tpId == 0 {
							fmt.Println("error 153")
							os.Exit(1)
						}

						stratum_hash := "." + lotStateName + "." + esrdStateName + "." + hivStateName
						stratum_id := Query.Stratum_id_by_hash[stratum_hash]
						tp_by_stratum_id := Query.Tp_stratum_id_by_tp_and_stratum[tpId][stratum_id]
						tp_by_stratum := &Inputs.TransitionProbabilitiesByStratum[tp_by_stratum_id]

						var true_tp float64

						if testingInfectedStateName == "Infected Testing TST" {
							if lotStateName == "Not Foreign-born" {
								true_tp = UsbTstSensitivity.Value * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveTstLtbiTest.Value
							} else {
								true_tp = FbTstSensitivity.Value * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveTstLtbiTest.Value
							}
						} else if testingInfectedStateName == "Infected Testing QFT" {
							if lotStateName == "Not Foreign-born" {
								true_tp = UsbQftSensitivity.Value * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveQftTspotTest.Value
							} else {
								true_tp = FbQftSensitivity.Value * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveQftTspotTest.Value
							}
						} else if testingInfectedStateName == "Infected Testing TSPOT" {
							if lotStateName == "Not Foreign-born" {
								true_tp = UsbTspotSensitivity.Value * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveQftTspotTest.Value
							} else {
								true_tp = FbTspotSensitivity.Value * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveQftTspotTest.Value
							}
						} else {
							true_tp = 99.0
						}

						// if has HIV, override
						if hivStateName != "Uninfected HIV" {
							if testingInfectedStateName == "Infected Testing TST" {
								true_tp = HivTstSensitivity.Value * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveTstLtbiTest.Value
							} else if testingInfectedStateName == "Infected Testing QFT" {
								true_tp = HivQftSensitivity.Value * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveQftTspotTest.Value
							} else if testingInfectedStateName == "Infected Testing TSPOT" {
								true_tp = HivTspotSensitivity.Value * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveQftTspotTest.Value
							} else {
								true_tp = 99.0
							}
						}

						// if has ESRD, override
						if esrdStateName == "ESRD" {
							if testingInfectedStateName == "Infected Testing TST" {
								true_tp = EsrdTstSensitivity.Value * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveTstLtbiTest.Value
							} else if testingInfectedStateName == "Infected Testing QFT" {
								true_tp = EsrdQftSensitivity.Value * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveQftTspotTest.Value
							} else if testingInfectedStateName == "Infected Testing TSPOT" {
								true_tp = EsrdTspotSensitivity.Value * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveQftTspotTest.Value
							} else {
								true_tp = 99.0
							}
						}

						tp_by_stratum.Base = true_tp
						// fmt.Println(testingInfectedStateName, ";", treatmentInfectedStateName, ";", lotStateName, ";", esrdStateName, ";", hivStateName, ";", true_tp)

					}

				}

				// true negatives
				for _, treatmentUninfectedStateName := range treatmentUninfectedStateNames {
					for _, testingUninfectedStateName := range testingUninfectedStateNames {

						// esrdState := Query.getStateByName(esrdStateName)
						// dmState := Query.getStateByName(dmStateName)
						// lotState := Query.getStateByName(lotStateName)
						treatmentUninfectedState := Query.getStateByName(treatmentUninfectedStateName)
						testingUninfectedState := Query.getStateByName(testingUninfectedStateName)

						tpId := Query.Tp_id_by_from_state_and_to_state[testingUninfectedState.Id][treatmentUninfectedState.Id]

						if tpId == 0 {
							fmt.Println("error 154")
							os.Exit(1)
						}

						stratum_hash := "." + lotStateName + "." + esrdStateName + "." + hivStateName
						stratum_id := Query.Stratum_id_by_hash[stratum_hash]
						tp_by_stratum_id := Query.Tp_stratum_id_by_tp_and_stratum[tpId][stratum_id]
						tp_by_stratum := &Inputs.TransitionProbabilitiesByStratum[tp_by_stratum_id]

						var true_tp float64

						if testingUninfectedStateName == "Uninfected Testing TST" {
							if lotStateName == "Not Foreign-born" {
								true_tp = (1.0 - UsbTstSpecificity.Value) * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveTstLtbiTest.Value
							} else {
								true_tp = (1.0 - FbTstSpecificity.Value) * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveTstLtbiTest.Value
							}
						} else if testingUninfectedStateName == "Uninfected Testing QFT" {
							if lotStateName == "Not Foreign-born" {
								true_tp = (1.0 - UsbQftSpecificity.Value) * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveQftTspotTest.Value
							} else {
								true_tp = (1.0 - FbQftSpecificity.Value) * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveQftTspotTest.Value
							}
						} else if testingUninfectedStateName == "Uninfected Testing TSPOT" {
							if lotStateName == "Not Foreign-born" {
								true_tp = (1.0 - UsbTspotSpecificity.Value) * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveQftTspotTest.Value
							} else {
								true_tp = (1.0 - FbTspotSpecificity.Value) * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveQftTspotTest.Value
							}
						} else {
							true_tp = 99.0
						}

						// if has HIV, override
						if hivStateName != "Uninfected HIV" {
							if testingUninfectedStateName == "Uninfected Testing TST" {
								true_tp = (1.0 - HivTstSpecificity.Value) * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveTstLtbiTest.Value
							} else if testingUninfectedStateName == "Uninfected Testing QFT" {
								true_tp = (1.0 - HivQftSpecificity.Value) * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveQftTspotTest.Value
							} else if testingUninfectedStateName == "Uninfected Testing TSPOT" {
								true_tp = (1.0 - HivTspotSpecificity.Value) * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveQftTspotTest.Value
							} else {
								true_tp = 99.0
							}
						}

						// if has ESRD, override
						if esrdStateName == "ESRD" {
							if testingUninfectedStateName == "Uninfected Testing TST" {
								true_tp = (1.0 - EsrdTstSpecificity.Value) * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveTstLtbiTest.Value
							} else if testingUninfectedStateName == "Uninfected Testing QFT" {
								true_tp = (1.0 - EsrdQftSpecificity.Value) * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveQftTspotTest.Value
							} else if testingUninfectedStateName == "Uninfected Testing TSPOT" {
								true_tp = (1.0 - EsrdTspotSpecificity.Value) * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveQftTspotTest.Value
							} else {
								true_tp = 99.0
							}
						}

						tp_by_stratum.Base = true_tp
						// fmt.Println(testingUninfectedStateName, ";", treatmentUninfectedStateName, ";", lotStateName, ";", esrdStateName, ";", hivStateName, ";", true_tp)

					}

				}

			}
		}
	}

	// ----------- false positives enrolling in treatment (this was system before was stratified)
	// conv["Uninfected Testing TST -> FP LBTI 9m INH - Month 1"] = (1.0 - SpecificityOfTst.Value) * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveTstLtbiTest.Value
	// conv["Uninfected Testing TST -> FP LTBI 6m INH - Month 1"] = (1.0 - SpecificityOfTst.Value) * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveTstLtbiTest.Value
	// conv["Uninfected Testing TST -> FP LTBI RIF - Month 1"] = (1.0 - SpecificityOfTst.Value) * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveTstLtbiTest.Value
	// conv["Uninfected Testing TST -> FP LTBI RTP - Month 1"] = (1.0 - SpecificityOfTst.Value) * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveTstLtbiTest.Value
	// conv["Uninfected Testing QFT -> FP LBTI 9m INH - Month 1"] = (1.0 - SpecificityOfQft.Value) * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveQftTspotTest.Value
	// conv["Uninfected Testing QFT -> FP LTBI 6m INH - Month 1"] = (1.0 - SpecificityOfQft.Value) * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveQftTspotTest.Value
	// conv["Uninfected Testing QFT -> FP LTBI RIF - Month 1"] = (1.0 - SpecificityOfQft.Value) * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveQftTspotTest.Value
	// conv["Uninfected Testing QFT -> FP LTBI RTP - Month 1"] = (1.0 - SpecificityOfQft.Value) * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveQftTspotTest.Value
	// conv["Uninfected Testing TSPOT -> FP LBTI 9m INH - Month 1"] = (1.0 - SpecificityOfTspot.Value) * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveQftTspotTest.Value
	// conv["Uninfected Testing TSPOT -> FP LTBI 6m INH - Month 1"] = (1.0 - SpecificityOfTspot.Value) * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveQftTspotTest.Value
	// conv["Uninfected Testing TSPOT -> FP LTBI RIF - Month 1"] = (1.0 - SpecificityOfTspot.Value) * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveQftTspotTest.Value
	// conv["Uninfected Testing TSPOT -> FP LTBI RTP - Month 1"] = (1.0 - SpecificityOfTspot.Value) * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveQftTspotTest.Value
	// conv["Uninfected Testing TST+QFT -> FP LBTI 9m INH - Month 1"] = (1.0 - SpecificityOfTstQft.Value) * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveQftTspotTest.Value
	// conv["Uninfected Testing TST+QFT -> FP LTBI 6m INH - Month 1"] = (1.0 - SpecificityOfTstQft.Value) * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveQftTspotTest.Value
	// conv["Uninfected Testing TST+QFT -> FP LTBI RIF - Month 1"] = (1.0 - SpecificityOfTstQft.Value) * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveQftTspotTest.Value
	// conv["Uninfected Testing TST+QFT -> FP LTBI RTP - Month 1"] = (1.0 - SpecificityOfTstQft.Value) * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveQftTspotTest.Value
	// conv["Uninfected Testing TST+TSPOT -> FP LBTI 9m INH - Month 1"] = (1.0 - SpecificityOfTstTspot.Value) * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveQftTspotTest.Value
	// conv["Uninfected Testing TST+TSPOT -> FP LTBI 6m INH - Month 1"] = (1.0 - SpecificityOfTstTspot.Value) * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveQftTspotTest.Value
	// conv["Uninfected Testing TST+TSPOT -> FP LTBI RIF - Month 1"] = (1.0 - SpecificityOfTstTspot.Value) * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveQftTspotTest.Value
	// conv["Uninfected Testing TST+TSPOT -> FP LTBI RTP - Month 1"] = (1.0 - SpecificityOfTstTspot.Value) * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveQftTspotTest.Value

	// conv["Fast latent -> Infected Testing TST"] = AccessMonthlyProportionOfTruePositivesThatAreTested.Value
	// conv["Fast latent -> Infected Testing QFT"] = AccessMonthlyProportionOfTruePositivesThatAreTested.Value
	// conv["Fast latent -> Infected Testing TSPOT"] = AccessMonthlyProportionOfTruePositivesThatAreTested.Value
	// conv["Fast latent -> Infected Testing TST+QFT"] = AccessMonthlyProportionOfTruePositivesThatAreTested.Value
	// conv["Fast latent -> Infected Testing TST+TSPOT"] = AccessMonthlyProportionOfTruePositivesThatAreTested.Value
	// conv["Slow latent -> Infected Testing TST"] = AccessMonthlyProportionOfTruePositivesThatAreTested.Value
	// conv["Slow latent -> Infected Testing QFT"] = AccessMonthlyProportionOfTruePositivesThatAreTested.Value
	// conv["Slow latent -> Infected Testing TSPOT"] = AccessMonthlyProportionOfTruePositivesThatAreTested.Value
	// conv["Slow latent -> Infected Testing TST+QFT"] = AccessMonthlyProportionOfTruePositivesThatAreTested.Value
	// conv["Slow latent -> Infected Testing TST+TSPOT"] = AccessMonthlyProportionOfTruePositivesThatAreTested.Value

	// (this was system before was stratified)
	// conv["Infected Testing TST -> LBTI 9m INH - Month 1"] = SensitivityOfTst.Value * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveTstLtbiTest.Value
	// conv["Infected Testing TST -> LTBI 6m INH - Month 1"] = SensitivityOfTst.Value * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveTstLtbiTest.Value
	// conv["Infected Testing TST -> LTBI RIF - Month 1"] = SensitivityOfTst.Value * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveTstLtbiTest.Value
	// conv["Infected Testing TST -> LTBI RTP - Month 1"] = SensitivityOfTst.Value * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveTstLtbiTest.Value
	// conv["Infected Testing QFT -> LBTI 9m INH - Month 1"] = SensitivityOfQft.Value * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveQftTspotTest.Value
	// conv["Infected Testing QFT -> LTBI 6m INH - Month 1"] = SensitivityOfQft.Value * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveQftTspotTest.Value
	// conv["Infected Testing QFT -> LTBI RIF - Month 1"] = SensitivityOfQft.Value * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveQftTspotTest.Value
	// conv["Infected Testing QFT -> LTBI RTP - Month 1"] = SensitivityOfQft.Value * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveQftTspotTest.Value
	// conv["Infected Testing TSPOT -> LBTI 9m INH - Month 1"] = SensitivityOfTspot.Value * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveQftTspotTest.Value
	// conv["Infected Testing TSPOT -> LTBI 6m INH - Month 1"] = SensitivityOfTspot.Value * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveQftTspotTest.Value
	// conv["Infected Testing TSPOT -> LTBI RIF - Month 1"] = SensitivityOfTspot.Value * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveQftTspotTest.Value
	// conv["Infected Testing TSPOT -> LTBI RTP - Month 1"] = SensitivityOfTspot.Value * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveQftTspotTest.Value
	// conv["Infected Testing TST+QFT -> LBTI 9m INH - Month 1"] = SensitivityOfTstQft.Value * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveQftTspotTest.Value
	// conv["Infected Testing TST+QFT -> LTBI 6m INH - Month 1"] = SensitivityOfTstQft.Value * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveQftTspotTest.Value
	// conv["Infected Testing TST+QFT -> LTBI RIF - Month 1"] = SensitivityOfTstQft.Value * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveQftTspotTest.Value
	// conv["Infected Testing TST+QFT -> LTBI RTP - Month 1"] = SensitivityOfTstQft.Value * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveQftTspotTest.Value
	// conv["Infected Testing TST+TSPOT -> LBTI 9m INH - Month 1"] = SensitivityOfTstTspot.Value * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveQftTspotTest.Value
	// conv["Infected Testing TST+TSPOT -> LTBI 6m INH - Month 1"] = SensitivityOfTstTspot.Value * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveQftTspotTest.Value
	// conv["Infected Testing TST+TSPOT -> LTBI RIF - Month 1"] = SensitivityOfTstTspot.Value * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveQftTspotTest.Value
	// conv["Infected Testing TST+TSPOT -> LTBI RTP - Month 1"] = SensitivityOfTstTspot.Value * ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveQftTspotTest.Value

	// ----------- post-treatment efficacy

	conv["LTBI treated with INH 9m -> Active - untreated"] = BaseRiskOfProgression.Value * (1 - EfficacyOf9H.Value)
	conv["LTBI treated with INH 6m -> Active - untreated"] = BaseRiskOfProgression.Value * (1 - EfficacyOf6H.Value)
	conv["LTBI treated with RIF -> Active - untreated"] = BaseRiskOfProgression.Value * (1 - EfficacyOf4R.Value)
	conv["LTBI treated with RTP -> Active - untreated"] = BaseRiskOfProgression.Value * (1 - EfficacyOf3Hp.Value)

	for k, v := range conv {
		as := strings.Split(k, " -> ")
		conv_from_state_name := as[0]
		conv_to_state_name := as[1]
		for i, tp := range Inputs.TransitionProbabilities {
			to_state_id := tp.To_state_id
			from_state_id := tp.From_state_id
			to_state_name := Inputs.States[to_state_id].Name
			from_state_name := Inputs.States[from_state_id].Name
			if conv_from_state_name == from_state_name && conv_to_state_name == to_state_name {
				//fmt.Println("saving from ", conv_from_state_name, " to ", conv_to_state_name, " as ", v)
				Inputs.TransitionProbabilities[i].Tp_base = v
			}

		}
	}

}

func check_sum_1(sum float64) {
	if sum != 1 {
		fmt.Println("error on variable calculation")
		os.Exit(1)
	}
}
