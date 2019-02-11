from app import *




db.session.query(Variable).delete()
db.session.commit()


variable_names = [
    "Access: monthly proportion of true negatives that are tested",
    "Access: monthly proportion of true positives that are tested",
    "USB TST Sensitivity",
    "USB TST Specificity",
    "USB QFT Sensitivity",
    "USB QFT Specificity",
    "USB TSPOT Sensitivity",
    "USB TSPOT Specificity",
    "FB TST Sensitivity",
    "FB TST Specificity",
    "FB QFT Sensitivity",
    "FB QFT Specificity",
    "FB TSPOT Sensitivity",
    "FB TSPOT Specificity",
    "HIV TST Sensitivity",
    "HIV TST Specificity",
    "HIV QFT Sensitivity",
    "HIV QFT Specificity",
    "HIV TSPOT Sensitivity",
    "HIV TSPOT Specificity",
    "ESRD TST Sensitivity",
    "ESRD TST Specificity",
    "ESRD QFT Sensitivity",
    "ESRD QFT Specificity",
    "ESRD TSPOT Sensitivity",
    "ESRD TSPOT Specificity",

    "Proportion of individuals that enroll in treatment after a positive TST LTBI test",
    "Proportion of individuals that enroll in treatment after a positive QFT/TSPOT test",
    "Number of LTBI cases caused by one active case",
    "Number of secondary TB cases caused by one active case",
    "Efficacy of 9H",
    "Efficacy of 6H",
    "Efficacy of 4R",
    "Efficacy of 3HP",
    "Base risk of progression",
    "Proportion of LTBI treated",
    "Fast latent progression",
    "Slow latent progression",
    "Total cost of LTBI treatment 9H",
    "Total cost of LTBI treatment 6H",
    "Total cost of LTBI treatment 4R",
    "Total cost of LTBI treatment 3HP",
    "Proportion of started who complete treatment, 9H",
    "Proportion of started who complete treatment, 6H",
    "Proportion of started who complete treatment, 4R",
    "Proportion of started who complete treatment, 3HP",
    "Cost of TST",
    "Cost of QFT",
    "Cost of TSPOT",
    "Cost of TST+QFT",
    "Cost of TST+TSPOT",
    "Cost of active TB case",
    "QALYs gained averting one case of active TB",
    "Discount",

# Calibration - beginning LTBI prevalence adjustments

    "LTBI overall adjustment starting",
    "LTBI overall FB adjustment starting",
    "LTBI overall USB adjustment starting",
    "LTBI Asian FB adjustment starting",
    "LTBI Asian USB adjustment starting",
    "LTBI White FB adjustment starting",
    "LTBI White USB adjustment starting",
    "LTBI Hispanic FB adjustment starting",
    "LTBI Hispanic USB adjustment starting",
    "LTBI Black FB adjustment starting",
    "LTBI Black USB adjustment starting",
    "LTBI Other FB adjustment starting",
    "LTBI Other USB adjustment starting",

# Calibration - beginning LTBI prevalence adjustments

    "LTBI overall adjustment",
    "LTBI overall FB adjustment",
    "LTBI overall USB adjustment",
    "LTBI Asian FB adjustment",
    "LTBI Asian USB adjustment",
    "LTBI White FB adjustment",
    "LTBI White USB adjustment",
    "LTBI Hispanic FB adjustment",
    "LTBI Hispanic USB adjustment",
    "LTBI Black FB adjustment",
    "LTBI Black USB adjustment",
    "LTBI Other FB adjustment",
    "LTBI Other USB adjustment",

# Calibration - risk factor adjustments

    "Diabetes prevalence adjustment",
    "ESRD prevalence adjustment",
    "Smoker prevalence adjustment",
    "TNF-alpha prevalence adjustment",
    "HIV prevalence adjustment",
    "Transplants prevalence adjustment",
    "Death rate prevalence adjustment",

    "Risk of progression calibrator",


# risk of progression calibration adjustments

    "Rop FB Asian adjustment",
    "Rop FB Black adjustment",
    "Rop FB Hispanic adjustment",
    "Rop FB Other adjustment",
    "Rop FB White adjustment",
    "Rop USB Asian adjustment",
    "Rop USB Black adjustment",
    "Rop USB Hispanic adjustment",
    "Rop USB Other adjustment",
    "Rop USB White adjustment",
    "Rop FB DM adjustment"

]

# LTBI testing access - positives
for variable_name in variable_names:
    print variable_name
    make_var(variable_name, 0.1, 0.005, 0.15)


print "------------------ MAKE SURE TO GET VARIABLES AFTER THIS ---------------"

