# R Analysis Script for Green Lab Project (Version with Pre-analysis Outlier Cleaning)

# --- 1. SETUP: Load Libraries ---
suppressPackageStartupMessages(library(tidyverse))
suppressPackageStartupMessages(library(rstatix))
suppressPackageStartupMessages(library(ggpubr))

theme_set(theme_minimal())

# --- 2. DATA LOADING AND PREPARATION ---
tryCatch({
  full_data <- read_csv("data/run_table.csv", show_col_types = FALSE)
}, error = function(e) {
  stop("Error: 'data/run_table.csv' not found. Make sure it's in the 'data/' directory.")
})

# --- 3. DATA CLEANING: REMOVE EXTREME OUTLIERS ---
# We use the IQR method to identify outliers. An outlier is a value
# outside of [Q1 - 1.5*IQR, Q3 + 1.5*IQR]. We will remove these for visualization.

# Calculate the number of rows before cleaning
initial_rows <- nrow(full_data)

# Identify outliers based on cpu_energy_j for each group
outlier_bounds <- full_data %>%
  group_by(benchmark, version, size) %>%
  summarise(
    Q1 = quantile(cpu_energy_j, 0.25, na.rm = TRUE),
    Q3 = quantile(cpu_energy_j, 0.75, na.rm = TRUE),
    IQR = Q3 - Q1,
    lower_bound = Q1 - 1.5 * IQR,
    upper_bound = Q3 + 1.5 * IQR,
    .groups = 'drop'
  )

# Join the bounds back to the main data and filter
# This cleaned_data will be used for PLOTTING
cleaned_data <- full_data %>%
  left_join(outlier_bounds, by = c("benchmark", "version", "size")) %>%
  filter(cpu_energy_j >= lower_bound & cpu_energy_j <= upper_bound) %>%
  select(-c(Q1, Q3, IQR, lower_bound, upper_bound)) # Remove temporary columns

# Calculate and report the number of removed outliers
final_rows <- nrow(cleaned_data)
outliers_removed <- initial_rows - final_rows
print(paste("Data Cleaning Complete. Removed", outliers_removed, "extreme outliers from", initial_rows, "total rows."))


# --- 4. DESCRIPTIVE STATISTICS (Calculated on the ORIGINAL data) ---
# We use the full, original dataset for statistics to report on what was actually measured.
descriptive_stats <- full_data %>%
  group_by(benchmark, version, size) %>%
  summarise(
    repetition_count = n(),
    avg_energy_j = mean(cpu_energy_j, na.rm = TRUE),
    median_energy_j = median(cpu_energy_j, na.rm = TRUE),
    sd_energy_j = sd(cpu_energy_j, na.rm = TRUE),
    avg_exec_time_sec = mean(exec_time_sec, na.rm = TRUE),
    avg_cpu_usage = mean(avg_cpu_usage, na.rm = TRUE),
    avg_memory_usage = mean(avg_used_memory, na.rm = TRUE),
    .groups = 'drop'
  )

write_csv(descriptive_stats, "data/descriptive_statistics.csv")
print("Successfully generated 'data/descriptive_statistics.csv' (based on full data)")

# --- 5. HYPOTHESIS TESTING & CORRELATIONS (Calculated on the ORIGINAL data) ---
# Non-parametric tests are robust to outliers, so we use the complete dataset for accuracy.
baseline_opt_data_full <- full_data %>%
  filter(version %in% c("baseline", "opt"))

rq1_hypothesis_tests <- baseline_opt_data_full %>%
  group_by(benchmark, size) %>%
  wilcox_test(cpu_energy_j ~ version, paired = TRUE) %>%
  adjust_pvalue(method = "bonferroni") %>%
  add_significance("p.adj")

write_csv(rq1_hypothesis_tests, "data/rq1_hypothesis_tests.csv")
print("Successfully generated 'data/rq1_hypothesis_tests.csv' (based on full data)")

rq2_correlation_analysis <- full_data %>%
  group_by(benchmark, version, size) %>%
  summarise(
    corr_energy_time = cor.test(cpu_energy_j, exec_time_sec, method = "spearman", exact = FALSE)$estimate,
    p_energy_time = cor.test(cpu_energy_j, exec_time_sec, method = "spearman", exact = FALSE)$p.value,
    corr_energy_cpu = cor.test(cpu_energy_j, avg_cpu_usage, method = "spearman", exact = FALSE)$estimate,
    p_energy_cpu = cor.test(cpu_energy_j, avg_cpu_usage, method = "spearman", exact = FALSE)$p.value,
    corr_energy_mem = cor.test(cpu_energy_j, avg_used_memory, method = "spearman", exact = FALSE)$estimate,
    p_energy_mem = cor.test(cpu_energy_j, avg_used_memory, method = "spearman", exact = FALSE)$p.value,
    .groups = 'drop'
  )

write_csv(rq2_correlation_analysis, "data/rq2_correlation_analysis.csv")
print("Successfully generated 'data/rq2_correlation_analysis.csv' (based on full data)")

# --- 6. VISUALIZATIONS (Using CLEANED data for plots) ---
cleaned_baseline_opt_data <- cleaned_data %>%
  filter(version %in% c("baseline", "opt"))

# --- Plot 1: LARGE Datasets ---
plot_data_large_cleaned <- cleaned_baseline_opt_data %>% filter(size == "large")

plot_rq1_large <- ggplot(plot_data_large_cleaned, aes(x = version, y = cpu_energy_j, color = version)) +
  geom_boxplot(outlier.shape = NA) +
  geom_jitter(width = 0.2, alpha = 0.7) +
  facet_wrap(~benchmark, scales = "free_y", ncol = 2) +
  stat_compare_means(data = baseline_opt_data_full %>% filter(size=="large"), aes(label = ..p.signif..), method = "wilcox.test", paired = TRUE) +
  labs(title = "Energy Consumption (Large Datasets): Baseline vs. Optimized Code", subtitle = "Note: Extreme outliers removed from plot for clarity. Statistics are based on full data.", x = "Code Version", y = "CPU Energy (Joules)") +
  theme(axis.text.x = element_text(angle = 45, hjust = 1), legend.position = "none") +
  scale_color_manual(values = c("#0073C2FF", "#EFC000FF"))

ggsave("data/plot_rq1_energy_large_datasets.png", plot_rq1_large, width = 12, height = 18, dpi = 300)
print("Successfully generated 'data/plot_rq1_energy_large_datasets.png'")

# --- Plot 2: SMALL Datasets ---
plot_data_small_cleaned <- cleaned_baseline_opt_data %>% filter(size == "small")

plot_rq1_small <- ggplot(plot_data_small_cleaned, aes(x = version, y = cpu_energy_j, color = version)) +
  geom_boxplot(outlier.shape = NA) +
  geom_jitter(width = 0.2, alpha = 0.7) +
  facet_wrap(~benchmark, scales = "free_y", ncol = 2) +
  stat_compare_means(data = baseline_opt_data_full %>% filter(size=="small"), aes(label = ..p.signif..), method = "wilcox.test", paired = TRUE) +
  labs(title = "Energy Consumption (Small Datasets): Baseline vs. Optimized Code", subtitle = "Note: Extreme outliers removed from plot for clarity. Statistics are based on full data.", x = "Code Version", y = "CPU Energy (Joules)") +
  theme(axis.text.x = element_text(angle = 45, hjust = 1), legend.position = "none") +
  scale_color_manual(values = c("#0073C2FF", "#EFC000FF"))

ggsave("data/plot_rq1_energy_small_datasets.png", plot_rq1_small, width = 12, height = 18, dpi = 300)
print("Successfully generated 'data/plot_rq1_energy_small_datasets.png'")

# --- Plot 3: RQ2 Correlation Scatter Plots (using FULL data) ---
# For scatter plots, it's often better to see all points, so we use the original data with log scales.
scatter_time <- ggplot(baseline_opt_data_full, aes(x = exec_time_sec, y = cpu_energy_j, color = version)) +
  geom_point(alpha = 0.6) + geom_smooth(method = "lm", se = FALSE, formula = y ~ x) +
  scale_x_log10() + scale_y_log10() + facet_wrap(~benchmark, scales = "free") +
  labs(title = "Energy vs. Execution Time", x = "Execution Time (s, log scale)", y = "Energy (J, log scale)")

scatter_cpu <- ggplot(baseline_opt_data_full, aes(x = avg_cpu_usage, y = cpu_energy_j, color = version)) +
  geom_point(alpha = 0.6) + geom_smooth(method = "lm", se = FALSE, formula = y ~ x) +
  facet_wrap(~benchmark, scales = "free") +
  labs(title = "Energy vs. CPU Usage", x = "Average CPU Usage (%)", y = "Energy (J)")

scatter_mem <- ggplot(baseline_opt_data_full, aes(x = avg_used_memory, y = cpu_energy_j, color = version)) +
  geom_point(alpha = 0.6) + geom_smooth(method = "lm", se = FALSE, formula = y ~ x) +
  facet_wrap(~benchmark, scales = "free") +
  labs(title = "Energy vs. Memory Usage", x = "Average Memory Usage (bytes)", y = "Energy (J)")

plot_rq2 <- ggarrange(scatter_time, scatter_cpu, scatter_mem, ncol = 1, nrow = 3, common.legend = TRUE, legend = "bottom")
final_plot_rq2 <- annotate_figure(plot_rq2, top = text_grob("Correlation Analysis (Baseline vs. Optimized Versions)", size = 16, face = "bold"))

ggsave("data/plot_rq2_correlation_scatter.png", final_plot_rq2, width = 16, height = 20, dpi = 300)
print("Successfully generated 'data/plot_rq2_correlation_scatter.png'")

print("--- Analysis Complete ---")