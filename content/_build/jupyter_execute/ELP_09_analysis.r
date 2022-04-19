require(reshape2) # For data handling
require(lme4) # Linear mixed-effects models
require(DHARMa) # Evaluate model fit
require(car) # Anova() function [instead of base R anova()]
require(emmeans) # Post-hoc analysis on the model

rm(list = ls()) # Remove variables/objects
graphics.off() # Close any open graphics

ELP_09 = read.csv("./Data/ELP_09_octopamine_side_learning_Y_maze.csv", header = TRUE, stringsAsFactors = FALSE, sep = ";")
head(ELP_09, n = 1) # Check if data was imported correctly

ELP_09$Solution = ifelse(ELP_09$Solution == "B", "0.01mM Octopamine", "Control")

ELP_09$Initial_Decision_Binary = ifelse(ELP_09$Initial_Decision == ELP_09$Reward_Side, 1, 0)
ELP_09$Final_Decision_Binary = ifelse(ELP_09$Final_Decision == ELP_09$Reward_Side, 1, 0)
ELP_09$Switched_Decision_Binary = ifelse(ELP_09$Initial_Decision_Binary == ELP_09$Final_Decision_Binary, 0, 1)
paste0("Ants switched their final decision in ", round(sum(ELP_09$Switched_Decision_Binary) / nrow(ELP_09) * 100, 0), "% of the visits!")

table(ELP_09$Solution, ELP_09$Reward_Side) / 4

for (i in 1:nrow(ELP_09)) {
  if (ELP_09$Visit[i] == "2" & !is.na(ELP_09$Bridge_Nest_Duration[i])) {
    if (ELP_09$Bridge_Nest_Duration[i] != ELP_09$Time_Since_Marking[i]) {
      print(paste0("Warning: Row ", i, " was changed from ", ELP_09$Bridge_Nest_Duration[i], "s to ", ELP_09$Time_Since_Marking[i], "s!"))
      ELP_09$Bridge_Nest_Duration[i] = ELP_09$Time_Since_Marking[i]
    }
  }
  else if (ELP_09$Visit[i] == "2" & is.na(ELP_09$Bridge_Nest_Duration[i])) {
    ELP_09$Bridge_Nest_Duration[i] = ELP_09$Time_Since_Marking[i]
    print(paste0("Warning: Row ", i, " was changed and Bridge_Nest_Duration was NA!"))
  }
}

for (i in 1:nrow(ELP_09)) {
  if (ELP_09$Time_Since_Marking[i] <= 1800) {
    ELP_09$TSM_Bin[i] = "0-30"
  }
  else if (ELP_09$Time_Since_Marking[i] > 1800 & ELP_09$Time_Since_Marking[i] <= 3600) {
    ELP_09$TSM_Bin[i] = "30-60"
  }
  else {
    print("Warning: Undefined bins!")
  }
}

table(ELP_09$Solution, ELP_09$TSM_Bin, ELP_09$Reward_Side) / 4

ELP_09$Collection_Date = as.factor(ELP_09$Collection_Date)
ELP_09$Time_Collection = as.factor(ELP_09$Time_Collection)
ELP_09$Experimentor = as.factor(ELP_09$Experimentor)
ELP_09$Starvation_Period = as.factor(ELP_09$Starvation_Period)
ELP_09$Donor_Colony = as.factor(ELP_09$Donor_Colony)
ELP_09$Recipient_Colony = as.factor(ELP_09$Recipient_Colony)

ELP_09$Visit = as.factor(ELP_09$Visit)
ELP_09$Solution = as.factor(ELP_09$Solution)
ELP_09$Solution = relevel(ELP_09$Solution, "Control")
ELP_09$Reward_Side = as.factor(ELP_09$Reward_Side)
ELP_09$TSM_Bin = as.factor(ELP_09$TSM_Bin)

ELP_09$Initial_Decision_Binary = as.factor(ELP_09$Initial_Decision_Binary)
ELP_09$Final_Decision_Binary = as.factor(ELP_09$Final_Decision_Binary)

initial_final_diff = melt(ELP_09, measure.vars = c("Initial_Decision_Binary", "Final_Decision_Binary"))
initial_final_diff$value = as.factor(initial_final_diff$value)
head(initial_final_diff, n = 1) # Check if data was imported correctly

diff_model = glmer(value ~ variable + (1|Starvation_Period) + (1|Experimentor/Collection_Date), data = initial_final_diff,family = binomial, glmerControl(optimizer = "bobyqa", optCtrl = list(maxfun = 1000000000)))
Anova(diff_model)

e = emmeans(diff_model, ~variable, type = "response")
pairs(e)

mod1 = glmer(Final_Decision_Binary ~ (Reward_Side + Solution + TSM_Bin + Visit)^2  +
               (1|Starvation_Period) + (1|Collection_Date), 
             data = ELP_09, family = "binomial", glmerControl(optimizer = "bobyqa", optCtrl = list(maxfun = 1000000000)))

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

mod4 = update(mod3, . ~ . - Solution:Visit)
anova(mod3, mod4)

summary(mod4)
Anova(mod4)
drop.scope(mod4)

mod5 = update(mod4, . ~ . - Reward_Side:Visit)
anova(mod4, mod5)

summary(mod5)
Anova(mod5)
drop.scope(mod5)

mod6 = update(mod5, . ~ . - TSM_Bin:Visit)
anova(mod5, mod6)

summary(mod6)
Anova(mod6)
drop.scope(mod6)

mod7 = update(mod6, . ~ . - Solution:TSM_Bin)
anova(mod6, mod7)

summary(mod7)
Anova(mod7)
drop.scope(mod7)

anova(mod1, mod7)
simres = simulateResiduals(mod6)
plot(simres, asFactor = T)

meanobj = emmeans(mod7, ~Reward_Side, type = "response")
pairs(meanobj, adjust = "bonferroni")

meanobj = emmeans(mod7, ~TSM_Bin * Visit, type = "response")
test(meanobj)

meanobj = emmeans(mod7, ~Solution, type = "response")
test(meanobj)
pairs(meanobj, adjust = "bonferroni")

meanobj = emmeans(mod7, ~1, type = "response")
test(meanobj)

sessionInfo()
