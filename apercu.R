# Aperçu du projet : Ballon d'Or 1976-2026
# Lancer depuis ce dossier : Rscript apercu.R  ->  APERCU.png (image) et APERCU.html (graphique interactif)
suppressPackageStartupMessages({library(dplyr); library(ggplot2); library(readr)})
theme_set(theme_minimal(base_size = 12) + theme(plot.title = element_text(face = "bold"), plot.title.position = "plot"))
if (!rmarkdown::pandoc_available() && dir.exists("/Applications/quarto/bin/tools")) Sys.setenv(RSTUDIO_PANDOC = "/Applications/quarto/bin/tools")
sauver <- function(p, w = 9, h = 5.5) {
  ggsave("APERCU.png", p, width = w, height = h, dpi = 150, bg = "white")
  i <- suppressWarnings(plotly::ggplotly(p)) %>% plotly::config(displaylogo = FALSE, locale = "fr")
  htmlwidgets::saveWidget(i, "APERCU.html", selfcontained = TRUE, title = p$labels$title)
  unlink("APERCU_files", recursive = TRUE)
}
b <- read_csv("ballon_dor_classements_1976_2026.csv", show_col_types = FALSE)
d <- b %>% filter(rank == 1, competition == "Ballon d'Or", sex == "Men") %>% count(player, sort = TRUE) %>% slice_head(n = 15)
p <- ggplot(d, aes(n, reorder(player, n))) + geom_col(fill = "#b7791f") + geom_text(aes(label = n), hjust = -0.3, size = 3.5) +
  scale_x_continuous(breaks = 0:8, expand = expansion(c(0, 0.1))) +
  labs(title = "Ballon d'Or masculin : les vainqueurs", subtitle = sprintf("%d-%d", min(b$year), max(b$year)), x = "Ballons d'Or", y = NULL)
sauver(p)
