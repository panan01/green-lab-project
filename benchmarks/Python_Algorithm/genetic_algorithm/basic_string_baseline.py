"""
Simple multithreaded algorithm to show how the 4 phases of a genetic algorithm works
(Evaluation, Selection, Crossover and Mutation)
https://en.wikipedia.org/wiki/Genetic_algorithm
Author: D4rkia
Modified by: Gemini
"""

from __future__ import annotations

import random
import argparse
import string

# Maximum size of the population.  Bigger could be faster but is more memory expensive.
N_POPULATION = 200
# Number of elements selected in every generation of evolution. The selection takes
# place from best to worst of that generation and must be smaller than N_POPULATION.
N_SELECTED = 50
# Probability that an element of a generation can mutate, changing one of its genes.
# This will guarantee that all genes will be used during evolution.
MUTATION_PROBABILITY = 0.4
# Just a seed to improve randomness required by the algorithm.
random.seed(random.randint(0, 1000))


def evaluate(item: str, main_target: str) -> tuple[str, float]:
    """
    Evaluate how similar the item is with the target by just
    counting each char in the right position
    >>> evaluate("Helxo Worlx", "Hello World")
    ('Helxo Worlx', 9.0)
    """
    score = len([g for position, g in enumerate(item) if g == main_target[position]])
    return (item, float(score))


def crossover(parent_1: str, parent_2: str) -> tuple[str, str]:
    """
    Slice and combine two strings at a random point.
    >>> random.seed(42)
    >>> crossover("123456", "abcdef")
    ('123def', 'abc456')
    """
    # Corrected crossover logic to produce more intuitive children
    random_slice = random.randint(0, len(parent_1))
    child_1 = parent_1[:random_slice] + parent_2[random_slice:]
    child_2 = parent_2[:random_slice] + parent_1[random_slice:]
    return (child_1, child_2)


def mutate(child: str, genes: list[str]) -> str:
    """
    Mutate a random gene of a child with another one from the list.
    >>> random.seed(123)
    >>> mutate("123456", list("ABCDEF"))
    '123C56'
    """
    child_list = list(child)
    if random.uniform(0, 1) < MUTATION_PROBABILITY:
        # Corrected index to avoid potential IndexError on empty strings
        if len(child_list) > 0:
            child_list[random.randint(0, len(child_list) - 1)] = random.choice(genes)
    return "".join(child_list)


# Select, crossover and mutate a new population.
def select(
    parent_1: tuple[str, float],
    population_score: list[tuple[str, float]],
    genes: list[str],
) -> list[str]:
    """
    Select the second parent and generate new population
    """
    pop = []
    # Generate more children proportionally to the fitness score.
    child_n = int(parent_1[1] * 10) + 1  # Simplified calculation for number of children
    child_n = 10 if child_n > 10 else child_n

    for _ in range(child_n):
        # Select the second parent from the top N_SELECTED individuals
        parent_2 = population_score[random.randint(0, N_SELECTED - 1)][0]

        child_1, child_2 = crossover(parent_1[0], parent_2)
        # Append new string to the population list.
        pop.append(mutate(child_1, genes))
        pop.append(mutate(child_2, genes))
    return pop


def run_genetic_algorithm(target: str, genes: list[str], debug: bool = True) -> tuple[int, int, str]:
    """
    Runs the main genetic algorithm loop.
    """

    # Verify if N_POPULATION is bigger than N_SELECTED
    if N_POPULATION < N_SELECTED:
        msg = f"N_POPULATION ({N_POPULATION}) must be bigger than N_SELECTED ({N_SELECTED})"
        raise ValueError(msg)
    # Verify that the target contains no genes besides the ones inside genes variable.
    not_in_genes_list = sorted({c for c in target if c not in genes})
    if not_in_genes_list:
        msg = f"{not_in_genes_list} is not in genes list, evolution cannot converge"
        raise ValueError(msg)

    # Generate random starting population.
    population = [
        "".join(random.choice(genes) for _ in range(len(target)))
        for _ in range(N_POPULATION)
    ]

    generation, total_population = 0, 0

    # This loop will end when we find a perfect match for our target.
    while True:
        generation += 1
        total_population += len(population)

        # Evaluation phase
        population_score = [evaluate(item, target) for item in population]

        # Sort population by score in descending order
        population_score = sorted(population_score, key=lambda x: x[1], reverse=True)

        # Check if a perfect match is found
        if population_score[0][0] == target:
            return (generation, total_population, population_score[0][0])

        # Print the best result every 10 generations.
        if debug and generation % 10 == 0:
            print(
                f"\nGeneration: {generation}"
                f"\nTotal Population: {total_population}"
                f"\nBest score: {population_score[0][1]}/{len(target)}"
                f"\nBest string: {population_score[0][0]}"
            )

        # --- SELECTION, CROSSOVER, MUTATION ---

        # Flush the old population, keeping some of the best evolutions (Elitism).
        # *** BUG FIX ***: Correctly select the best individuals from the *sorted* list.
        population_best = [item for item, score in population_score[: int(N_POPULATION / 3)]]
        population.clear()
        population.extend(population_best)
        
        # Normalize population score to be between 0 and 1 for selection.
        normalized_population_score = [
            (item, score / len(target)) for item, score in population_score
        ]

        # Select top individuals to be parents for the next generation.
        for i in range(N_SELECTED):
            # The 'select' function handles crossover and mutation internally
            population.extend(select(normalized_population_score[i], normalized_population_score, genes))
            # Limit the population size to N_POPULATION
            if len(population) > N_POPULATION:
                break
        
        # Ensure population does not exceed the maximum size
        population = population[:N_POPULATION]


def main(size: str) -> None:
    """
    Main function to run the genetic algorithm based on problem size.
    """
    print(f"Selected problem size: '{size}'")

    # Define problem size and parameters
    if size == "small":
        # A smaller target string for quicker execution
        target_str = "Hello World!"
    elif size == "large":
        # A larger target string for a more computationally intensive task
        target_str = (
            "This is a genetic algorithm to evaluate, combine, evolve, and mutate a string!"
        )
    else:
        # This case should not be reached due to argparse choices
        raise ValueError("Invalid size specified. Choose 'small' or 'large'.")

    # The gene pool must contain all characters present in the target string
    genes_list = list(string.ascii_letters + string.digits + string.punctuation + " ")
    
    print(f"Target: '{target_str}'")
    print("Starting evolution...")
    
    generation, population, target = run_genetic_algorithm(target_str, genes_list)
    
    print(
        f"\n----------------------------------"
        f"\nEvolution Finished!"
        f"\nGeneration: {generation}"
        f"\nTotal Population Processed: {population}"
        f"\nTarget Found: {target}"
        f"\n----------------------------------"
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="A simple Genetic Algorithm to find a target string.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "--size",
        choices=["small", "large"],
        required=True,
        help=(
            "Select the problem size for the algorithm:\n"
            "'small': A short target string ('Hello World!').\n"
            "'large': A much longer target string for a more intensive test."
        )
    )

    args = parser.parse_args()
    main(args.size)