getFullyQualifiedWindowsStylePath=$(shell cygpath --windows --absolute "$(1)")
unslashedDir=$(patsubst %/,%,$(dir $(1)))
pathOfThisMakefile=$(call unslashedDir,$(lastword $(MAKEFILE_LIST)))
pathOfHumanReadablePenTableScript:=${pathOfThisMakefile}/acad_plotstyle_manager.py
pathOfPenTableModule:=${pathOfThisMakefile}/acad_pentable.py

buildFolder:=${pathOfThisMakefile}/build
# sourceDirectory:=${pathOfThisMakefile}/../../../acad_support
sourceDirectory:=${pathOfThisMakefile}/test_fodder

sources:=$(wildcard ${sourceDirectory}/*.stb) $(wildcard ${sourceDirectory}/*.ctb)
# sources:=$(wildcard ${pathOfThisMakefile}/../../../acad_support/acad.stb)
# humanReadableFiles:=$(foreach source,${sources},${buildFolder}/$(basename $(notdir ${source})).json)
humanReadableFiles:=$(foreach source,${sources},${buildFolder}/$(notdir ${source}).json)

venv:=$(shell cd "$(abspath $(dir ${pathOfHumanReadablePenTableScript}))" > /dev/null 2>&1; pipenv --venv || echo initializeVenv)
# the variable 'venv' will evaluate to the path of the venv, if it exists, or else will evaluate to 'initializeVenv', which is a target that we have created below.
# in either case, we want to use venv as a prerequisite for default.

.PHONY: initializeVenv

.PHONY: default

# default: | ${buildFolder} ${venv}
# 	pipenv run python \
# 		"$(call getFullyQualifiedWindowsStylePath,${pathOfHumanReadablePenTableScript})" \
# 		--input_acad_pen_table_file="$(word 1,${sources})" \
# 		--output_human_readable_pen_table_file="$(call getFullyQualifiedWindowsStylePath,$(word 1,$(foreach source,${sources},${buildFolder}/$(basename $(notdir ${source})).json)))" 
	
default: ${humanReadableFiles} 
	@echo venv: ${venv}
	# autohotkey "U:\global hotkeys\executeInAutocad.ahk" --quiet "$(call getFullyQualifiedWindowsStylePath,${buildFolder}/sampler.lsp)"
	


# ${buildFolder}/%.json: ${sourceDirectory}/%.stb ${pathOfHumanReadablePenTableScript} | ${buildFolder} ${venv}


${buildFolder}/%.ctb.json: ${sourceDirectory}/%.ctb ${pathOfHumanReadablePenTableScript} ${pathOfPenTableModule} | ${buildFolder} ${venv}
	@echo "====== BUILDING $@ from $< ======= "
	pipenv run python \
		"$(call getFullyQualifiedWindowsStylePath,${pathOfHumanReadablePenTableScript})" \
		--input_acad_pen_table_file="$(call getFullyQualifiedWindowsStylePath,$<)" \
		--output_human_readable_pen_table_file="$(call getFullyQualifiedWindowsStylePath,$@)" 


${buildFolder}/%.stb.json: ${sourceDirectory}/%.stb ${pathOfHumanReadablePenTableScript} ${pathOfPenTableModule} | ${buildFolder} ${venv}
	@echo "====== BUILDING $@ from $< ======= "
	pipenv run python \
		"$(call getFullyQualifiedWindowsStylePath,${pathOfHumanReadablePenTableScript})" \
		--input_acad_pen_table_file="$(call getFullyQualifiedWindowsStylePath,$<)" \
		--output_human_readable_pen_table_file="$(call getFullyQualifiedWindowsStylePath,$@)" 



${buildFolder}:
	@echo "====== CREATING THE BUILD FOLDER ======="
	@echo "buildFolder: ${buildFolder}"
	mkdir --parents "${buildFolder}"
#buildFolder, when included as a prerequisite for rules, should be declared as an order-only prerequisites (by placing it to the right of a "|" character in the 
# list of prerequisites.  See https://www.gnu.org/software/make/manual/html_node/Prerequisite-Types.html 

${venv}: $(if $(filter-out initializeVenv,${venv}),$(dir ${pathOfHumanReadablePenTableScript})Pipfile $(dir ${pathOfHumanReadablePenTableScript})Pipfile.lock)
	@echo "====== INITIALIZING VIRTUAL ENVIRONMENT ======= "
	# @echo "venv: ${venv}"
	@echo "target: $@"
	# # @echo "prerequisites: $^"
	# @echo "prerequisites that are newer than the target: $?"
	# # @echo "prerequisites that are not newer than the target: $^ - $?"
	# @echo "prerequisites that are not newer than the target: $(filter-out $?,$^)"
	# @echo "order-only prerequisites: $|"
	cd "$(abspath $(dir ${pathOfHumanReadablePenTableScript}))"; pipenv install
	touch $(shell cd "$(abspath $(dir ${pathOfHumanReadablePenTableScript}))" > /dev/null 2>&1; pipenv --venv)

.SILENT:		


# SHELL=sh	
	