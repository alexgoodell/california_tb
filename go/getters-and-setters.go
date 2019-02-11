package main

import (
	"fmt"
	"os"
)

//////////////////////////// Getters and Setters /////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////

//  --------------- chain

// gets the uninitialized state for a chain (the state individuals start in)
func (chain *Chain) get_uninitialized_state() State {
	stateId := Query.Unintialized_state_by_chain[chain.Id]
	state := Inputs.States[stateId]
	return state
}

//  --------------- state

// get the transition probabilities *from* the given state. It's called
// destination because we're finding the chances of moving to each destination
func getDestinationProbabilities(stateId uint) []TransitionProbability {

	// need to copy to avoid passing a slice with pointer!
	tpsToReturn := make([]TransitionProbability, len(Query.Tps_by_from_state[stateId]), len(Query.Tps_by_from_state[stateId]))
	copy(tpsToReturn, Query.Tps_by_from_state[stateId])
	return tpsToReturn
}

// get any interactions that will effect the transtion from
// the persons current states based on all states that they are
// in - it is a method of their current state in this chain,
// and accepts an array of all currents states they occupy
func (fromState State) get_relevant_interactions(allStates []State) []Interaction {

	var relevantInteractions []Interaction
	var interactionIds []uint
	for _, inState := range allStates {
		interactionIds = append(interactionIds, Query.getInteractionIds(inState, fromState)...)
	}
	for _, interactionId := range interactionIds {
		relevantInteractions = append(relevantInteractions, Inputs.Interactions[interactionId])
	}

	var toState []uint
	if len(relevantInteractions) > 0 {
		for relevantInteractionId := range relevantInteractions {
			toState = append(toState, Inputs.Interactions[relevantInteractionId].To_state_id)
		}
		//fmt.Println(toState)
		//pause()
	}
	_ = toState

	// :i is faster than append()
	return relevantInteractions

}

func get_state_by_id(stateId uint) State {

	theState := Inputs.States[stateId]

	if theState.Id == stateId {
		return theState
	}

	fmt.Println("Cannot find state by id ", stateId)
	os.Exit(1)
	return theState

}

// func getYLLFromDeath(person Person, cycle Cycle) float64 {
// 	agesChain := Query.getChainByName("Age")
// 	ageState := person.get_state_by_chain(agesChain, cycle)
// 	sexChain := Query.getChainByName("Sex")
// 	sexState := person.get_state_by_chain(sexChain, cycle)
// 	return Query.getLifeExpectancyBySexAge(sexState, ageState)
// }

func getDeathStateByChain(chain Chain) State {
	deathStateId := Query.Death_state_by_chain[chain.Id]
	deathState := get_state_by_id(deathStateId)
	return deathState
}

func (Query *Query_t) getChainByName(name string) Chain {
	chainId := Query.chain_id_by_name[name]
	chain := Inputs.Chains[chainId]
	if chain.Name != name {
		fmt.Println("problem getting chain by name: ", name, " does not exist")
		os.Exit(1)
	}
	return chain
}

func (Query *Query_t) getStateByName(name string) State {
	stateId := Query.state_id_by_name[name]
	state := Inputs.States[stateId]
	if state.Name != name {
		fmt.Println("problem getting state by name: ", name, " does not exist")
		fmt.Println("only found", state)
		os.Exit(1)
	}
	return state
}

// func (Query *Query_t) getLifeExpectancyBySexAge(sex State, age State) float64 {
// 	//Use struct as map key
// 	key := SexAge{sex.Id, age.Id}
// 	le := Query.Life_expectancy_by_sex_and_age[key]
// 	return le
// }

func (Query *Query_t) getInteractionIds(inState State, fromState State) []uint {
	//Use struct as map key
	var key InteractionKey
	var interactionIdsToReturn []uint
	key.In_state_id = inState.Id
	key.From_state_id = fromState.Id
	interactionIds := Query.interaction_ids_by_in_state_and_from_state[key]
	for _, interactionId := range interactionIds {
		interaction := &Inputs.Interactions[interactionId]
		if interaction.From_state_id == fromState.Id && interaction.In_state_id == inState.Id {
			interactionIdsToReturn = append(interactionIdsToReturn, interaction.Id)
		}
	}

	// if len(interactionIdsToReturn) > 0 {
	// 	//fmt.Println(interactionIdsToReturn[0:1])
	// 	return interactionIdsToReturn[0:1]
	// }

	return interactionIdsToReturn
}

// get the current state of the person in this chain (should be the uninitialized state for cycle 0)
func (thisPerson *Person) get_state_by_chain(thisChain Chain, cycle Cycle) State {
	thisChainId := thisChain.Id
	var stateToReturn State
	var stateToReturnId uint
	// fmt.Println(thisPerson.Id, thisChainId)
	stateToReturnId = Query.Master_record_current_cycle_by_person_and_chain[thisPerson.Id][thisChainId].State_id
	stateToReturn = Inputs.States[stateToReturnId]
	if stateToReturn.Id == stateToReturnId {
		return stateToReturn
	}
	fmt.Println("Cannot find state via get_state_by_chain, error 2")
	os.Exit(1)
	return stateToReturn
}

// get all states this person is in at the current cycle
func (thisPerson *Person) get_states(cycle Cycle) []State {
	var statesToReturnIds []uint
	for ch := 0; ch < len(Inputs.Chains); ch++ {
		statesToReturnIds = append(statesToReturnIds, Query.Master_record_current_cycle_by_person_and_chain[thisPerson.Id][ch].State_id)
	}
	thisPersonId := thisPerson.Id
	// statesToReturnIds := Query.State_id_by_cycle_and_person_and_chain[cycle.Id][thisPersonId]
	statesToReturn := make([]State, len(statesToReturnIds), len(statesToReturnIds))
	for i, statesToReturnId := range statesToReturnIds {
		if Inputs.States[statesToReturnId].Id == statesToReturnId {
			statesToReturn[i] = Inputs.States[statesToReturnId]
		} else {
			fmt.Println("cannot find states via get_states, cycle & person id =", cycle.Id, thisPersonId)
			fmt.Println("looking for id", statesToReturnId, "but found", Inputs.States[statesToReturnId].Id)
			os.Exit(1)
		}
	}
	if len(statesToReturn) > 0 {
		return statesToReturn
	} else {
		fmt.Println("cannot find states via get_states")
		os.Exit(1)
		return statesToReturn
	}
}
