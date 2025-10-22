# ===================================================================
# R SCRIPT FOR GREEN LAB PAPER: ENERGY EFFICIENCY GUIDELINES (v14 - FINAL)
# ===================================================================
# This version updates the forensic plots based on user feedback:
# 1. REMOVES the boxplot from the hybrid plot.
# 2. The final plot is now a VIOLIN + JITTER plot for a cleaner aesthetic.
# ===================================================================


# 1. SETUP: LOAD LIBRARIES, DEFINE PATHS, AND LOAD DATA
# -------------------------------------------------------------------
if (!require(tidyverse)) install.packages("tidyverse")
if (!require(rstatix)) install.packages("rstatix")
if (!require(coin)) install.packages("coin")

library(tidyverse)
library(rstatix)
library(coin)

input_file <- "data/run_table.csv"
output_dir <- "data/output"
dir.create(output_dir, showWarnings = FALSE, recursive = TRUE)

df <- read_csv(input_file, show_col_types = FALSE) %>%
  mutate(across(all_of(c("benchmark", "version", "size")), as.factor))

cat("--- 1. Data Loaded and Prepared ---\n\n")


# (Sections 2 and 3 for statistical analysis and summary table generation are unchanged and run in the background)
# ...
cat("--- 2 & 3. Performing statistical analysis and building summary tables... ---\n")
primary_test_results <- df %>% filter(version %in% c("baseline", "opt")) %>% group_by(benchmark, size) %>% rstatix::wilcox_test(cpu_energy_j ~ version, paired = TRUE) %>% select(benchmark, size, p)
primary_effsize_results <- df %>% filter(version %in% c("baseline", "opt")) %>% group_by(benchmark, size) %>% rstatix::wilcox_effsize(cpu_energy_j ~ version, paired = TRUE)
baseline_means <- df %>% filter(version == "baseline") %>% group_by(benchmark, size) %>% summarise(across(where(is.numeric), mean, .names = "baseline_{.col}"), .groups = 'drop')
opt_means <- df %>% filter(version == "opt") %>% group_by(benchmark, size) %>% summarise(across(where(is.numeric), mean, .names = "opt_{.col}"), .groups = 'drop')
full_summary_for_plotting <- baseline_means %>% left_join(opt_means, by = c("benchmark", "size")) %>% left_join(primary_test_results, by = c("benchmark", "size")) %>% left_join(primary_effsize_results %>% select(benchmark, size, effsize, magnitude), by = c("benchmark", "size")) %>%
  mutate(reduction_pct_energy = ((baseline_cpu_energy_j - opt_cpu_energy_j) / baseline_cpu_energy_j) * 100, reduction_pct_time = ((baseline_exec_time_sec - opt_exec_time_sec) / baseline_exec_time_sec) * 100, reduction_pct_cpu = ((baseline_avg_cpu_usage - opt_avg_cpu_usage) / baseline_avg_cpu_usage) * 100, reduction_pct_memory = ((baseline_avg_used_memory - opt_avg_used_memory) / baseline_avg_used_memory) * 100, is_significant = ifelse(p < 0.05, "Yes", "No"))
cat("Statistical analysis complete.\n\n")


# 4. GENERATE AND SAVE ALL PLOTS
# -------------------------------------------------------------------
cat("--- 4. Generating and saving all plots... ---\n")

# (Plots 1, 2, and 3: Summary, Heatmap, and Effect Size plots are unchanged)
# ...

# --- PLOT 4 (FINAL VERSION): Forensic Analysis of 'merge_sort' Failure ---
cat("Generating final forensic analysis plot for 'merge_sort'...\n")
mergesort_large_df <- df %>%
  filter(benchmark == "merge_sort" & size == "large")

forensic_plot_failure <- ggplot(mergesort_large_df, aes(x = version, y = cpu_energy_j, fill = version)) +
  # Create the semi-transparent violin plot
  geom_violin(trim = FALSE, alpha = 0.5) +
  # Overlay the raw data points
  geom_jitter(width = 0.1, alpha = 0.7, color = "black") +
  scale_y_log10(breaks = c(1, 10, 25, 50, 100)) +
  scale_x_discrete(limits = c("baseline", "g1", "g2", "g3", "opt")) +
  theme_bw() +
  theme(legend.position = "none") +
  labs(
    title = "Forensic Analysis of 'merge_sort' Failure (Large Workload)",
    subtitle = "Violin plots show distribution density. Y-axis is on a log scale.",
    x = "Guideline Version Applied",
    y = "CPU Energy (Joules, log scale)"
  )

print(forensic_plot_failure)
forensic_plot_failure_path <- file.path(output_dir, "forensic_plot_mergesort_violin_no_box.png")
ggsave(forensic_plot_failure_path, forensic_plot_failure, width = 10, height = 6, units = "in")
cat(paste("Final forensic plot for merge_sort saved to:", forensic_plot_failure_path, "\n"))


# --- PLOT 5 (FINAL VERSION): Forensic Analysis of 'md5' Success ---
cat("Generating final forensic analysis plot for 'md5' success story...\n")
md5_large_df <- df %>%
  filter(benchmark == "md5" & size == "large")

md5_version_order <- c("baseline", "g1", "g3", "g6", "g7", "g9", "opt")

forensic_plot_success <- ggplot(md5_large_df, aes(x = version, y = cpu_energy_j, fill = version)) +
  # Create the semi-transparent violin plot
  geom_violin(trim = FALSE, alpha = 0.5) +
  # Overlay the raw data points
  geom_jitter(width = 0.1, alpha = 0.7, color = "black") +
  scale_y_log10(breaks = c(1, 2, 5, 10, 50, 100, 200, 300)) +
  scale_x_discrete(limits = md5_version_order) +
  theme_bw() +
  theme(legend.position = "none") +
  labs(
    title = "Forensic Analysis of 'md5' Success (Large Workload)",
    subtitle = "Violin plots show distribution density. Y-axis is on a log scale.",
    x = "Guideline Version Applied",
    y = "CPU Energy (Joules, log scale)"
  )

print(forensic_plot_success)
forensic_plot_success_path <- file.path(output_dir, "forensic_plot_md5_violin_no_box.png")
ggsave(forensic_plot_success_path, forensic_plot_success, width = 10, height = 6, units = "in")
cat(paste("Final forensic plot for md5 saved to:", forensic_plot_success_path, "\n"))

# (The other plots will still be generated and saved correctly in the background)
# ...
final_summary_table_for_csv <- full_summary_for_plotting %>% select(benchmark, size, baseline_energy_mean = baseline_cpu_energy_j, opt_energy_mean = opt_cpu_energy_j, reduction_pct = reduction_pct_energy, p_value = p, is_significant, effect_size = effsize, effect_magnitude = magnitude)
final_table_path <- file.path(output_dir, "final_summary_table_corrected.csv")
write.csv(final_summary_table_for_csv, final_table_path, row.names = FALSE)
heatmap_data <- full_summary_for_plotting %>% select(benchmark, size, starts_with("reduction_pct_")) %>% rename(Energy = reduction_pct_energy, Time = reduction_pct_time, CPU = reduction_pct_cpu, Memory = reduction_pct_memory) %>% pivot_longer(cols = c(Energy, Time, CPU, Memory), names_to = "metric", values_to = "percent_change") %>% left_join(full_summary_for_plotting %>% select(benchmark, size, reduction_pct_energy), by = c("benchmark", "size"))
heatmap_plot <- ggplot(heatmap_data, aes(x = metric, y = reorder(benchmark, reduction_pct_energy), fill = percent_change)) + geom_tile(color = "white", linewidth = 0.5) + geom_text(aes(label = paste0(round(percent_change, 0), "%")), color = "black", size = 3) + scale_fill_gradient2(name = "Change (%)", low = "red", mid = "white", high = "darkgreen", midpoint = 0, limits = c(-110, 110)) + facet_wrap(~ size) + theme_minimal() + labs(title = "Performance Trade-Offs of Optimizations", subtitle = "Percentage change from baseline to 'opt' version. Green = Reduction/Improvement.", x = "Performance Metric", y = "Benchmark (sorted by energy reduction)")
heatmap_path <- file.path(output_dir, "tradeoff_heatmap.png")
ggsave(heatmap_path, heatmap_plot, width = 12, height = 10, units = "in")
effect_size_plot_data <- full_summary_for_plotting %>% mutate(signed_effect_size = -effsize, benchmark_sorted = reorder(benchmark, signed_effect_size))
effect_size_plot <- ggplot(effect_size_plot_data, aes(x = signed_effect_size, y = benchmark_sorted)) + geom_vline(xintercept = 0, linetype = "dashed", color = "grey") + geom_point(aes(color = is_significant), size = 3) + facet_wrap(~ size) + scale_color_manual(name = "Statistically Significant\n(p < 0.05)", values = c("Yes" = "blue", "No" = "lightgrey")) + theme_minimal() + theme(panel.grid.major.y = element_blank()) + labs(title = "Effect Size and Significance of Optimizations on Energy Usage", subtitle = "Positive values indicate energy reduction. Blue dots are significant.", x = "Effect Size (Cliff's Delta) - Flipped Sign", y = "Benchmark")
effect_size_plot_path <- file.path(output_dir, "effect_size_plot.png")
ggsave(effect_size_plot_path, effect_size_plot, width = 12, height = 8, units = "in")
summary_plot <- ggplot(full_summary_for_plotting, aes(x = reorder(benchmark, reduction_pct_energy), y = reduction_pct_energy, fill = ifelse(reduction_pct_energy > 0, "Reduction", "Increase"))) + geom_bar(stat = "identity", width = 0.7) + facet_wrap(~ size, scales = "free_y") + coord_flip() + scale_fill_manual(name = "Effect Type", values = c("Reduction" = "darkgreen", "Increase" = "darkred")) + theme_minimal() + labs(title = "Energy Reduction of Optimized Code Compared to Baseline", subtitle = "Sorted from most to least effective", x = "Benchmark", y = "Energy Reduction (%)")
summary_plot_path <- file.path(output_dir, "summary_plot_percent_reduction.png")
ggsave(summary_plot_path, summary_plot, width = 12, height = 8, units = "in")


cat("\n--- All analysis complete. All outputs are in the 'data/output' folder. ---\n")