require(reshape2) # For data handling
require(lme4) # Linear mixed-effects models
require(DHARMa) # Evaluate model fit
require(car) # Anova() function [instead of base R anova()]
require(emmeans) # Post-hoc analysis on the model

rm(list = ls()) # Remove variables/objects
graphics.off() # Close any open graphics

ELP_08 = read.csv("./Data/ELP_08_caffeine_side_learning_Y_maze.csv", header = TRUE, stringsAsFactors = FALSE, sep = ";")
head(ELP_08, n = 1) # Check if data was imported correctly

ELP_08$Solution = ifelse(ELP_08$Solution == "B", "250ppm Caffeine", "Control")

ELP_08$Initial_Decision_Binary = ifelse(ELP_08$Initial_Decision == ELP_08$Reward_Side, 1, 0)
ELP_08$Final_Decision_Binary = ifelse(ELP_08$Final_Decision == ELP_08$Reward_Side, 1, 0)
ELP_08$Switched_Decision_Binary = ifelse(ELP_08$Initial_Decision_Binary == ELP_08$Final_Decision_Binary, 0, 1)
paste0("Ants switched their final decision in ", round(sum(ELP_08$Switched_Decision_Binary) / nrow(ELP_08) * 100, 0), "% of the visits!")

table(ELP_08$Solution, ELP_08$Reward_Side) / 4

for (i in 1:nrow(ELP_08)) {
  if (ELP_08$Visit[i] == "2" & !is.na(ELP_08$Bridge_Nest_Duration[i])) {
    if (ELP_08$Bridge_Nest_Duration[i] != ELP_08$Time_Since_Marking[i]) {
      print(paste0("Warning: Row ", i, " was changed from ", ELP_08$Bridge_Nest_Duration[i], "s to ", ELP_08$Time_Since_Marking[i], "s!"))
      ELP_08$Bridge_Nest_Duration[i] = ELP_08$Time_Since_Marking[i]
    }
  }
  else if (ELP_08$Visit[i] == "2" & is.na(ELP_08$Bridge_Nest_Duration[i])) {
    ELP_08$Bridge_Nest_Duration[i] = ELP_08$Time_Since_Marking[i]
    print(paste0("Warning: Row ", i, " was changed and Bridge_Nest_Duration was NA!"))
  }
}

for (i in 1:nrow(ELP_08)) {
  if (ELP_08$Time_Since_Marking[i] <= 1800) {
    ELP_08$TSM_Bin[i] = "0-30"
  }
  else if (ELP_08$Time_Since_Marking[i] > 1800 & ELP_08$Time_Since_Marking[i] <= 3600) {
    ELP_08$TSM_Bin[i] = "30-60"
  }
  else if (ELP_08$Time_Since_Marking[i] > 3600 & ELP_08$Time_Since_Marking[i] <= 5400) {
    ELP_08$TSM_Bin[i] = "60-90"
  }
  else if (ELP_08$Time_Since_Marking[i] > 5400 & ELP_08$Time_Since_Marking[i] <= 7200) {
    ELP_08$TSM_Bin[i] = "90-120"
  }
  else if (ELP_08$Time_Since_Marking[i] > 7200) {
    ELP_08$TSM_Bin[i] = "120+"
  }
  else {
    print("Warning: Undefined bins!")
  }
}

table(ELP_08$Solution, ELP_08$TSM_Bin, ELP_08$Reward_Side) / 4

ELP_08$Collection_Date = as.factor(ELP_08$Collection_Date)
ELP_08$Time_Collection = as.factor(ELP_08$Time_Collection)
ELP_08$Experimentor = as.factor(ELP_08$Experimentor)
ELP_08$Starvation_Period = as.factor(ELP_08$Starvation_Period)
ELP_08$Donor_Colony = as.factor(ELP_08$Donor_Colony)
ELP_08$Recipient_Colony = as.factor(ELP_08$Recipient_Colony)

ELP_08$Visit = as.factor(ELP_08$Visit)
ELP_08$Solution = as.factor(ELP_08$Solution)
ELP_08$Solution = relevel(ELP_08$Solution, "Control")
ELP_08$Reward_Side = as.factor(ELP_08$Reward_Side)
ELP_08$TSM_Bin = as.factor(ELP_08$TSM_Bin)

ELP_08$Initial_Decision_Binary = as.factor(ELP_08$Initial_Decision_Binary)
ELP_08$Final_Decision_Binary = as.factor(ELP_08$Final_Decision_Binary)

initial_final_diff = melt(ELP_08, measure.vars = c("Initial_Decision_Binary", "Final_Decision_Binary"))
initial_final_diff$value = as.factor(initial_final_diff$value)
head(initial_final_diff, n = 1) # Check if data was imported correctly

diff_model = glmer(value ~ variable + (1|Starvation_Period) + (1|Experimentor/Collection_Date), data = initial_final_diff,family = binomial, glmerControl(optimizer = "bobyqa", optCtrl = list(maxfun = 1000000000)))
Anova(diff_model)

e = emmeans(diff_model, ~variable, type = "response")
pairs(e)

mod1 = glmer(Final_Decision_Binary ~ (Reward_Side + Solution + TSM_Bin + Visit)^2  +
               (1|Starvation_Period) + (1|Experimentor/Collection_Date), 
             data = ELP_08, family = "binomial", glmerControl(optimizer = "bobyqa", optCtrl = list(maxfun = 1000000000)))

simres = simulateResiduals(mod1)
plot(simres, asFactor = T)

summary(mod1)
Anova(mod1)
drop.scope(mod1)

mod2 = update(mod1, . ~ . - Reward_Side:TSM_Bin)
anova(mod1, mod2)

summary(mod2)
Anova(mod2)
drop.scope(mod2)

mod3 = update(mod2, . ~ . - Reward_Side:Solution)
anova(mod2, mod3)

summary(mod3)
Anova(mod3)
drop.scope(mod3)

mod4 = update(mod3, . ~ . - Reward_Side:Visit)
anova(mod3, mod4)

summary(mod4)
Anova(mod4)
drop.scope(mod4)

mod5 = update(mod4, . ~ . - Solution:TSM_Bin)
anova(mod4, mod5)

summary(mod5)
Anova(mod5)
drop.scope(mod5)

mod6 = update(mod5, . ~ . - Solution:Visit)
anova(mod5, mod6)

summary(mod6)
Anova(mod6)
drop.scope(mod6)

anova(mod1, mod6)
simres = simulateResiduals(mod6)
plot(simres, asFactor = T)

meanobj = emmeans(mod6, ~Reward_Side, type = "response")
pairs(meanobj, adjust = "bonferroni")

meanobj = emmeans(mod6, ~TSM_Bin * Visit, type = "response")
test(meanobj)

meanobj = emmeans(mod6, ~Solution, type = "response")
test(meanobj)
pairs(meanobj, adjust = "bonferroni")

meanobj = emmeans(mod6, ~1, type = "response")
test(meanobj)

sessionInfo()
