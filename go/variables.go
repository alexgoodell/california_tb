package main

import (
	"fmt"

	"github.com/jinzhu/gorm"
)

var AccessMonthlyProportionOfTrueNegativesThatAreTested  Variable
var AccessMonthlyProportionOfTruePositivesThatAreTested  Variable
var UsbTstSensitivity  Variable
var UsbTstSpecificity  Variable
var UsbQftSensitivity  Variable
var UsbQftSpecificity  Variable
var UsbTspotSensitivity  Variable
var UsbTspotSpecificity  Variable
var FbTstSensitivity  Variable
var FbTstSpecificity  Variable
var FbQftSensitivity  Variable
var FbQftSpecificity  Variable
var FbTspotSensitivity  Variable
var FbTspotSpecificity  Variable
var HivTstSensitivity  Variable
var HivTstSpecificity  Variable
var HivQftSensitivity  Variable
var HivQftSpecificity  Variable
var HivTspotSensitivity  Variable
var HivTspotSpecificity  Variable
var EsrdTstSensitivity  Variable
var EsrdTstSpecificity  Variable
var EsrdQftSensitivity  Variable
var EsrdQftSpecificity  Variable
var EsrdTspotSensitivity  Variable
var EsrdTspotSpecificity  Variable
var ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveTstLtbiTest  Variable
var ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveQftTspotTest  Variable
var NumberOfLtbiCasesCausedByOneActiveCase  Variable
var NumberOfSecondaryTbCasesCausedByOneActiveCase  Variable
var EfficacyOf9H  Variable
var EfficacyOf6H  Variable
var EfficacyOf4R  Variable
var EfficacyOf3Hp  Variable
var BaseRiskOfProgression  Variable
var ProportionOfLtbiTreated  Variable
var FastLatentProgression  Variable
var SlowLatentProgression  Variable
var TotalCostOfLtbiTreatment9H  Variable
var TotalCostOfLtbiTreatment6H  Variable
var TotalCostOfLtbiTreatment4R  Variable
var TotalCostOfLtbiTreatment3Hp  Variable
var ProportionOfStartedWhoCompleteTreatment9H  Variable
var ProportionOfStartedWhoCompleteTreatment6H  Variable
var ProportionOfStartedWhoCompleteTreatment4R  Variable
var ProportionOfStartedWhoCompleteTreatment3Hp  Variable
var CostOfTst  Variable
var CostOfQft  Variable
var CostOfTspot  Variable
var CostOfTstQft  Variable
var CostOfTstTspot  Variable
var CostOfActiveTbCase  Variable
var QalysGainedAvertingOneCaseOfActiveTb  Variable
var LtbiOverallAdjustmentStarting  Variable
var LtbiOverallFbAdjustmentStarting  Variable
var LtbiOverallUsbAdjustmentStarting  Variable
var LtbiAsianFbAdjustmentStarting  Variable
var LtbiAsianUsbAdjustmentStarting  Variable
var LtbiWhiteFbAdjustmentStarting  Variable
var LtbiWhiteUsbAdjustmentStarting  Variable
var LtbiHispanicFbAdjustmentStarting  Variable
var LtbiHispanicUsbAdjustmentStarting  Variable
var LtbiBlackFbAdjustmentStarting  Variable
var LtbiBlackUsbAdjustmentStarting  Variable
var LtbiOtherFbAdjustmentStarting  Variable
var LtbiOtherUsbAdjustmentStarting  Variable
var LtbiOverallAdjustment  Variable
var LtbiOverallFbAdjustment  Variable
var LtbiOverallUsbAdjustment  Variable
var LtbiAsianFbAdjustment  Variable
var LtbiAsianUsbAdjustment  Variable
var LtbiWhiteFbAdjustment  Variable
var LtbiWhiteUsbAdjustment  Variable
var LtbiHispanicFbAdjustment  Variable
var LtbiHispanicUsbAdjustment  Variable
var LtbiBlackFbAdjustment  Variable
var LtbiBlackUsbAdjustment  Variable
var LtbiOtherFbAdjustment  Variable
var LtbiOtherUsbAdjustment  Variable
var DiabetesPrevalenceAdjustment  Variable
var EsrdPrevalenceAdjustment  Variable
var SmokerPrevalenceAdjustment  Variable
var TnfAlphaPrevalenceAdjustment  Variable
var HivPrevalenceAdjustment  Variable
var TransplantsPrevalenceAdjustment  Variable
var RiskOfProgressionCalibrator  Variable
var RopFbAsianAdjustment  Variable
var RopFbBlackAdjustment  Variable
var RopFbHispanicAdjustment  Variable
var RopFbOtherAdjustment  Variable
var RopFbWhiteAdjustment  Variable
var RopUsbAsianAdjustment  Variable
var RopUsbBlackAdjustment  Variable
var RopUsbHispanicAdjustment  Variable
var RopUsbOtherAdjustment  Variable
var RopUsbWhiteAdjustment  Variable
var RopFbDmAdjustment  Variable
var Discount  Variable

func initializeVariables() {

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

	/////// DYNAMICALLY GENERATED DO NOT TOUCH BELOW THIS LINE //////////
	

	db.Where("name = ?", "Access: monthly proportion of true negatives that are tested").First(&AccessMonthlyProportionOfTrueNegativesThatAreTested)
	db.Where("name = ?", "Access: monthly proportion of true positives that are tested").First(&AccessMonthlyProportionOfTruePositivesThatAreTested)
	db.Where("name = ?", "USB TST Sensitivity").First(&UsbTstSensitivity)
	db.Where("name = ?", "USB TST Specificity").First(&UsbTstSpecificity)
	db.Where("name = ?", "USB QFT Sensitivity").First(&UsbQftSensitivity)
	db.Where("name = ?", "USB QFT Specificity").First(&UsbQftSpecificity)
	db.Where("name = ?", "USB TSPOT Sensitivity").First(&UsbTspotSensitivity)
	db.Where("name = ?", "USB TSPOT Specificity").First(&UsbTspotSpecificity)
	db.Where("name = ?", "FB TST Sensitivity").First(&FbTstSensitivity)
	db.Where("name = ?", "FB TST Specificity").First(&FbTstSpecificity)
	db.Where("name = ?", "FB QFT Sensitivity").First(&FbQftSensitivity)
	db.Where("name = ?", "FB QFT Specificity").First(&FbQftSpecificity)
	db.Where("name = ?", "FB TSPOT Sensitivity").First(&FbTspotSensitivity)
	db.Where("name = ?", "FB TSPOT Specificity").First(&FbTspotSpecificity)
	db.Where("name = ?", "HIV TST Sensitivity").First(&HivTstSensitivity)
	db.Where("name = ?", "HIV TST Specificity").First(&HivTstSpecificity)
	db.Where("name = ?", "HIV QFT Sensitivity").First(&HivQftSensitivity)
	db.Where("name = ?", "HIV QFT Specificity").First(&HivQftSpecificity)
	db.Where("name = ?", "HIV TSPOT Sensitivity").First(&HivTspotSensitivity)
	db.Where("name = ?", "HIV TSPOT Specificity").First(&HivTspotSpecificity)
	db.Where("name = ?", "ESRD TST Sensitivity").First(&EsrdTstSensitivity)
	db.Where("name = ?", "ESRD TST Specificity").First(&EsrdTstSpecificity)
	db.Where("name = ?", "ESRD QFT Sensitivity").First(&EsrdQftSensitivity)
	db.Where("name = ?", "ESRD QFT Specificity").First(&EsrdQftSpecificity)
	db.Where("name = ?", "ESRD TSPOT Sensitivity").First(&EsrdTspotSensitivity)
	db.Where("name = ?", "ESRD TSPOT Specificity").First(&EsrdTspotSpecificity)
	db.Where("name = ?", "Proportion of individuals that enroll in treatment after a positive TST LTBI test").First(&ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveTstLtbiTest)
	db.Where("name = ?", "Proportion of individuals that enroll in treatment after a positive QFT/TSPOT test").First(&ProportionOfIndividualsThatEnrollInTreatmentAfterAPositiveQftTspotTest)
	db.Where("name = ?", "Number of LTBI cases caused by one active case").First(&NumberOfLtbiCasesCausedByOneActiveCase)
	db.Where("name = ?", "Number of secondary TB cases caused by one active case").First(&NumberOfSecondaryTbCasesCausedByOneActiveCase)
	db.Where("name = ?", "Efficacy of 9H").First(&EfficacyOf9H)
	db.Where("name = ?", "Efficacy of 6H").First(&EfficacyOf6H)
	db.Where("name = ?", "Efficacy of 4R").First(&EfficacyOf4R)
	db.Where("name = ?", "Efficacy of 3HP").First(&EfficacyOf3Hp)
	db.Where("name = ?", "Base risk of progression").First(&BaseRiskOfProgression)
	db.Where("name = ?", "Proportion of LTBI treated").First(&ProportionOfLtbiTreated)
	db.Where("name = ?", "Fast latent progression").First(&FastLatentProgression)
	db.Where("name = ?", "Slow latent progression").First(&SlowLatentProgression)
	db.Where("name = ?", "Total cost of LTBI treatment 9H").First(&TotalCostOfLtbiTreatment9H)
	db.Where("name = ?", "Total cost of LTBI treatment 6H").First(&TotalCostOfLtbiTreatment6H)
	db.Where("name = ?", "Total cost of LTBI treatment 4R").First(&TotalCostOfLtbiTreatment4R)
	db.Where("name = ?", "Total cost of LTBI treatment 3HP").First(&TotalCostOfLtbiTreatment3Hp)
	db.Where("name = ?", "Proportion of started who complete treatment, 9H").First(&ProportionOfStartedWhoCompleteTreatment9H)
	db.Where("name = ?", "Proportion of started who complete treatment, 6H").First(&ProportionOfStartedWhoCompleteTreatment6H)
	db.Where("name = ?", "Proportion of started who complete treatment, 4R").First(&ProportionOfStartedWhoCompleteTreatment4R)
	db.Where("name = ?", "Proportion of started who complete treatment, 3HP").First(&ProportionOfStartedWhoCompleteTreatment3Hp)
	db.Where("name = ?", "Cost of TST").First(&CostOfTst)
	db.Where("name = ?", "Cost of QFT").First(&CostOfQft)
	db.Where("name = ?", "Cost of TSPOT").First(&CostOfTspot)
	db.Where("name = ?", "Cost of TST+QFT").First(&CostOfTstQft)
	db.Where("name = ?", "Cost of TST+TSPOT").First(&CostOfTstTspot)
	db.Where("name = ?", "Cost of active TB case").First(&CostOfActiveTbCase)
	db.Where("name = ?", "QALYs gained averting one case of active TB").First(&QalysGainedAvertingOneCaseOfActiveTb)
	db.Where("name = ?", "LTBI overall adjustment starting").First(&LtbiOverallAdjustmentStarting)
	db.Where("name = ?", "LTBI overall FB adjustment starting").First(&LtbiOverallFbAdjustmentStarting)
	db.Where("name = ?", "LTBI overall USB adjustment starting").First(&LtbiOverallUsbAdjustmentStarting)
	db.Where("name = ?", "LTBI Asian FB adjustment starting").First(&LtbiAsianFbAdjustmentStarting)
	db.Where("name = ?", "LTBI Asian USB adjustment starting").First(&LtbiAsianUsbAdjustmentStarting)
	db.Where("name = ?", "LTBI White FB adjustment starting").First(&LtbiWhiteFbAdjustmentStarting)
	db.Where("name = ?", "LTBI White USB adjustment starting").First(&LtbiWhiteUsbAdjustmentStarting)
	db.Where("name = ?", "LTBI Hispanic FB adjustment starting").First(&LtbiHispanicFbAdjustmentStarting)
	db.Where("name = ?", "LTBI Hispanic USB adjustment starting").First(&LtbiHispanicUsbAdjustmentStarting)
	db.Where("name = ?", "LTBI Black FB adjustment starting").First(&LtbiBlackFbAdjustmentStarting)
	db.Where("name = ?", "LTBI Black USB adjustment starting").First(&LtbiBlackUsbAdjustmentStarting)
	db.Where("name = ?", "LTBI Other FB adjustment starting").First(&LtbiOtherFbAdjustmentStarting)
	db.Where("name = ?", "LTBI Other USB adjustment starting").First(&LtbiOtherUsbAdjustmentStarting)
	db.Where("name = ?", "LTBI overall adjustment").First(&LtbiOverallAdjustment)
	db.Where("name = ?", "LTBI overall FB adjustment").First(&LtbiOverallFbAdjustment)
	db.Where("name = ?", "LTBI overall USB adjustment").First(&LtbiOverallUsbAdjustment)
	db.Where("name = ?", "LTBI Asian FB adjustment").First(&LtbiAsianFbAdjustment)
	db.Where("name = ?", "LTBI Asian USB adjustment").First(&LtbiAsianUsbAdjustment)
	db.Where("name = ?", "LTBI White FB adjustment").First(&LtbiWhiteFbAdjustment)
	db.Where("name = ?", "LTBI White USB adjustment").First(&LtbiWhiteUsbAdjustment)
	db.Where("name = ?", "LTBI Hispanic FB adjustment").First(&LtbiHispanicFbAdjustment)
	db.Where("name = ?", "LTBI Hispanic USB adjustment").First(&LtbiHispanicUsbAdjustment)
	db.Where("name = ?", "LTBI Black FB adjustment").First(&LtbiBlackFbAdjustment)
	db.Where("name = ?", "LTBI Black USB adjustment").First(&LtbiBlackUsbAdjustment)
	db.Where("name = ?", "LTBI Other FB adjustment").First(&LtbiOtherFbAdjustment)
	db.Where("name = ?", "LTBI Other USB adjustment").First(&LtbiOtherUsbAdjustment)
	db.Where("name = ?", "Diabetes prevalence adjustment").First(&DiabetesPrevalenceAdjustment)
	db.Where("name = ?", "ESRD prevalence adjustment").First(&EsrdPrevalenceAdjustment)
	db.Where("name = ?", "Smoker prevalence adjustment").First(&SmokerPrevalenceAdjustment)
	db.Where("name = ?", "TNF-alpha prevalence adjustment").First(&TnfAlphaPrevalenceAdjustment)
	db.Where("name = ?", "HIV prevalence adjustment").First(&HivPrevalenceAdjustment)
	db.Where("name = ?", "Transplants prevalence adjustment").First(&TransplantsPrevalenceAdjustment)
	db.Where("name = ?", "Risk of progression calibrator").First(&RiskOfProgressionCalibrator)
	db.Where("name = ?", "Rop FB Asian adjustment").First(&RopFbAsianAdjustment)
	db.Where("name = ?", "Rop FB Black adjustment").First(&RopFbBlackAdjustment)
	db.Where("name = ?", "Rop FB Hispanic adjustment").First(&RopFbHispanicAdjustment)
	db.Where("name = ?", "Rop FB Other adjustment").First(&RopFbOtherAdjustment)
	db.Where("name = ?", "Rop FB White adjustment").First(&RopFbWhiteAdjustment)
	db.Where("name = ?", "Rop USB Asian adjustment").First(&RopUsbAsianAdjustment)
	db.Where("name = ?", "Rop USB Black adjustment").First(&RopUsbBlackAdjustment)
	db.Where("name = ?", "Rop USB Hispanic adjustment").First(&RopUsbHispanicAdjustment)
	db.Where("name = ?", "Rop USB Other adjustment").First(&RopUsbOtherAdjustment)
	db.Where("name = ?", "Rop USB White adjustment").First(&RopUsbWhiteAdjustment)
	db.Where("name = ?", "Rop FB DM adjustment").First(&RopFbDmAdjustment)
	db.Where("name = ?", "Discount").First(&Discount)

	/////// DYNAMICALLY GENERATED DO NOT TOUCH ABOVE THIS LINE //////////

}
