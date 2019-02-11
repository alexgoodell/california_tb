package main

// ---------------- Stratification system

// This describes a type of cross-section of the population, such as "gender - ethnicity - age"
type Stratum_type struct {
	Id   uint
	Name string
}

// This describes a specific grouping of people, for example "men - African American - 25 years old"
type Stratum struct {
	Id              uint
	Name            string
	Stratum_type_id uint
	//stratum hash is just a useful way for go
	// to quickly find the correct row (stratum)
	// it is a state list divided by .'s. Ie, "43.23.54.2"
	Stratum_hash string
}

// table name for gorm
func (c Stratum) TableName() string {
	return "strata"
}

// This specifies which chains (aka models) are a part of a stratum type, for
// example, for the statum type "gender - ethnicity - age", there would be
//  three rows in stratum_type_content: gender, ethnicity, and age.
type Stratum_type_content struct {
	Id              uint
	Stratum_type_id uint
	Chain_id        uint
}

// This specifies which *states* are associated with a stratum. For example,
// the stratum "men - African American - 25 years old" would have three rows:
// men state, African american state, and 25 years old state
type Stratum_content struct {
	Id         uint
	Stratum_id uint
	Chain_id   uint
	State_id   uint
}

// This specifes a specific TP for a specifc statrum of individuals. For example,
// it might look something like this:
//
//   | from_state | to_state | stratum                    | base | low  | high |
//   +------------+----------+----------------------------+------+------+------+
//   | no diabtes | diabetes | white-male-25yo            | 0.1  | 0.05 | 0.2  |
//   | no diabtes | diabetes | african-american-male-25yo | 0.2  | 0.1  | 0.3  |
//

type Transition_probability_by_stratum struct {
	Id                        uint
	Stratum_id                uint
	From_state_id             uint
	To_state_id               uint
	Base                      float64
	Low                       float64
	High                      float64
	Transition_probability_id uint
}

func (c Transition_probability_by_stratum) TableName() string {
	return "transition_probabilities_by_stratum"
}

// following is not currently used
// This specifes a specific variable for a specifc statrum of individuals. For example,
// it might look something like this:
//
//   | variableId | stratum                    | base | low  | high |
//   +------------+----------------------------+------+------+------+
//   | risk of X  | white-male-25yo            | 0.1  | 0.05 | 0.2  |
//   | risk of X  | african-american-male-25yo | 0.2  | 0.1  | 0.3  |

type Variable_by_stratum struct {
	Id          uint
	Stratum_id  uint
	Variable_id uint
	Base        float64
	Low         float64
	High        float64
}

func (c Variable_by_stratum) TableName() string {
	return "variables_by_stratum"
}

//////// --------------- basic types -----------------////////
type Variable struct {
	Id            uint
	Name          string
	Value         float64
	Low           float64
	High          float64
	Original_base float64
}

type MasterRecord struct {
	Cycle_id                  uint
	Person_id                 uint
	State_id                  uint
	Chain_id                  uint
	NegQaly                   float64
	Ylds                      float64
	Ylls                      float64
	Costs                     float64
	Has_entered_simulation    bool
	State_name                string //TODO remove
	Is_tracked                bool   // this represents when someone enters a state
	Entered_from_state        uint
	RiskOfProgression         float64
	Months_life_remaining     float64
	Age                       float64
	Months_since_TB_infection uint
	Risk_of_infection         float64

	//through a "tracked" transition, such as TB -> death "TB mortality"
	// or unifected -> TB "infection"
}

type InteractionKey struct {
	In_state_id   uint
	From_state_id uint
}

//TODO rename to costs per state
type Cost struct {
	Id         uint
	State_id   uint
	State_name string
	Costs      float64
	//PSA_id   uint
}

type DisabilityWeight struct {
	Id                uint
	State_id          uint
	Disability_weight float64
	//PSA_id            uint
}

type State struct {
	Id                     uint
	Chain_id               uint
	Name                   string
	Is_uninitialized_state bool
	Is_death_state         bool
	Is_tunnel              bool
	Is_medical_risk_factor bool
	Tunnel_target_id       uint
}

type Intervention struct {
	Id             uint
	Name           string
	Testing_groups []struct {
		Begin_cycle            uint
		End_cycle              uint
		Id                     uint
		Monthly_testing_uptake float64
		Name                   string
		Criteria               []struct {
			Chain_name  string
			State_names []string
		}
		Test_choice_pos      string
		Test_choice_neg      string
		Treatment_choice_pos string
		Treatment_choice_neg string
	}
}

type Transition_probability_by_intervention struct {
	Id                      uint
	Intervention_id         uint
	Transition_probility_id uint
	Replacement_tp          float64
}

// table name for gorm
func (c Transition_probability_by_intervention) TableName() string {
	return "transition_probabilities_by_intervention"
}

type Chain struct {
	Id   uint
	Name string
}

type Cycle struct {
	Id   uint
	Name string
	Year uint
}

type Person struct {
	Id                     uint
	Age                    float64
	YearsInUs              float64
	MonthsSinceTBInfection float64
	RiskOfProgression      float64
	HasMedicalRiskFactor   bool
	TestingGroupId         uint
	LastTbTest             uint
	IsHcw                  bool
}

type Interaction struct {
	Id                uint
	In_state_id       uint
	From_state_id     uint
	To_state_id       uint
	Adjustment        float64
	Effected_chain_id uint
	Description       string
	// PSA_id            uint
}

type TransitionProbability struct {
	Id                    uint
	From_state_id         uint
	To_state_id           uint
	Tp_base               float64
	Is_dynamic            bool
	Dynamic_function_name string
	Is_stratified         bool
	Stratum_type_id       uint
	Is_tracked            bool
	Original_base         float64 //used for PSA
	Low                   float64
	High                  float64
	// PSA_id  uint
}

type Input struct {
	Variables                           []Variable
	Chains                              []Chain
	People                              []Person
	States                              []State
	TransitionProbabilities             []TransitionProbability
	Interactions                        []Interaction
	Cycles                              []Cycle
	MasterRecords                       []MasterRecord
	CurrentCycle                        []MasterRecord
	NextCycle                           []MasterRecord
	Costs                               []Cost
	DisabilityWeights                   []DisabilityWeight
	StratumTypes                        []Stratum_type
	Strata                              []Stratum
	StratumTypeContents                 []Stratum_type_content
	StratumContents                     []Stratum_content
	TransitionProbabilitiesByStratum    []Transition_probability_by_stratum
	VariablesByStratum                  []Variable_by_stratum
	Synchronizations                    []Synchronization
	Interventions                       []Intervention
	TransitionProbabiliesByIntervention []Transition_probability_by_intervention
	BaseInitLines                       []BaseInitLine
	// InterventionsInfo                   []InterventionInfo
	// LifeExpectancies        []LifeExpectancy
	// TPByRASs                []TPByRAS
	// InterventionValues      []InterventionValue
	// RegressionRates         []RegressionRate
	// PsaInputs               []PsaInput
	// DsaInputs               []DsaInput
}

type OutputByCycleState struct {
	Id                         uint
	Ylls                       float64
	Ylds                       float64
	Population                 uint
	Population_fb              uint
	Population_us              uint
	Costs                      float64
	Dalys                      float64
	Cycle_id                   uint
	Chain_id                   uint
	State_id                   uint
	Intervention_id            uint
	Intervention_name          string
	Active_cases_fb            uint
	Slow_latents_fb            uint
	Fast_latents_fb            uint
	Active_cases_us            uint
	Slow_latents_us            uint
	Fast_latents_us            uint
	Risk_of_prog_us            float64
	Risk_of_prog_fb            float64
	Months_life_remaining_us   float64
	Months_life_remaining_fb   float64
	Iteration_num              uint
	Psa_iteration_num          int
	State_name                 string
	Age                        float64
	Recent_transmission_us     uint
	Recent_transmission_fb     uint
	Recent_transmission_us_rop float64
	Recent_transmission_fb_rop float64
	Transmission_within_us     uint
	Risk_of_infection_fb       float64
	Risk_of_infection_us       float64
	Year                       uint
	HCW_in_state               uint
}

type OutputByCycleStateLimited struct {
	Iteration_num              uint
	Population                 uint
	Population_us              uint
	Population_fb              uint
	Costs                      float64
	Cycle_id                   uint
	State_id                   uint
	Intervention_id            uint
	Intervention_name          string
	Risk_of_prog_us            float64
	Risk_of_prog_fb            float64
	Months_life_remaining_us   float64
	Months_life_remaining_fb   float64
	Psa_iteration_num          int
	State_name                 string
	Age                        float64
	Year                       uint
	Recent_transmission_fb     uint
	Recent_transmission_fb_rop float64
	Recent_transmission_us     uint
	Recent_transmission_us_rop float64
	HCW_in_state               uint
}

// table name for gorm
func (c OutputByCycleState) TableName() string {
	return "outputs_by_cycle_state"
}

type OutputByCycle struct {
	Cycle_id   uint
	Test_costs uint
}

type Output struct {
	OutputsByCycleStateFull []OutputByCycleState
	OutputsByCycleStatePsa  []OutputByCycleState
	OutputsByCycle          []OutputByCycle
}

type Query_t struct {

	// this is a slice of integers representing rows of the BaseInitLines, but
	// are duplicated according to the weights from IPUMS. It allows us to
	// sample randomly from the current population (at the start of the model)
	// and from entering individuals (per year)
	Random_sample_current map[int][]uint
	Random_sample_new     map[int][]uint

	Has_interaction_by_state_id                     []bool
	Master_record_current_cycle_by_person_and_chain [][]MasterRecord
	Master_record_next_cycle_by_person_and_chain    [][]MasterRecord
	State_id_has_stratified_tp                      []bool
	// transmission
	LTBI_risk_by_cycle_isUsb_and_race        [][][]float64
	Num_active_cases_by_cycle_isUsb_and_race [][][]float64
	Num_susceptible_by_cycle_isUsb_and_race  [][][]uint
	Total_susceptible_by_cycle               []uint
	Total_active_by_cycle                    []float64
	Total_population_by_cycle                []uint
	Low_from_age_group                       map[string]uint
	High_from_age_group                      map[string]uint
	//State_id_by_cycle_and_person_and_chain          [][][]uint
	States_ids_by_cycle_and_person                 [][]uint
	Tps_by_from_state                              [][]TransitionProbability // TODO: Change to Tp_ids_by [Issue: https://github.com/alexgoodell/go-mdism/issues/58]
	Tp_id_by_from_state_and_to_state               [][]uint
	interaction_ids_by_in_state_and_from_state     map[InteractionKey][]uint
	State_populations_by_cycle                     [][]uint
	Chain_id_by_state                              []uint
	Death_state_by_chain                           []uint
	Cost_by_state_id                               []float64
	Disability_weight_by_state_id                  []float64
	Master_record_id_by_cycle_and_person_and_chain [][][]uint
	Stratum_id_by_hash                             map[string]uint
	Unintialized_state_by_chain                    []uint
	Outputs_id_by_cycle_and_state                  [][]uint
	Tp_stratum_id_by_tp_and_stratum                [][]uint
	Chain_ids_by_stratum_type_id                   [][]uint
	Synchronization_to_states_by_trigger_state     [][]uint

	// used for comparison in calibration
	Life_expectancy_by_sex_and_age map[string]map[string]float64
	Iteration_year_group           []map[string]map[string]map[string]float64
	Year_group_avg                 map[string]map[string]map[string]float64
	Year_group_avg_rvct            map[string]map[string]map[string]float64

	// used for printing to python (for charting) in calibration
	OutputYears []OutputYear

	// Unexported and used by the "getters"
	chain_id_by_name map[string]uint
	state_id_by_name map[string]uint
}

// this is used for calibration
type OutputYear struct {
	Id                 uint
	Year               string
	Group              string
	CasesAllIterations float64
	CasesAverage       float64
	Nativity           string
}

type Synchronization struct {
	Trigger_state_id uint
	To_state_id      uint
}

type BaseInitLine struct {
	Id                  uint
	Sex                 string
	Race                string
	Age_group           string
	Years_in_us         string
	Citizen             string
	Birthplace          string
	Weight2001          uint
	Weight2014          uint
	WeightNewPeople2001 uint
	WeightNewPeople2002 uint
	WeightNewPeople2003 uint
	WeightNewPeople2004 uint
	WeightNewPeople2005 uint
	WeightNewPeople2006 uint
	WeightNewPeople2007 uint
	WeightNewPeople2008 uint
	WeightNewPeople2009 uint
	WeightNewPeople2010 uint
	WeightNewPeople2011 uint
	WeightNewPeople2012 uint
	WeightNewPeople2013 uint
	WeightNewPeople2014 uint
}

// table name for gorm
func (c BaseInitLine) TableName() string {
	return "base_init_lines"
}
