#!/usr/bin/python3

# Written by Sukhada. Email: sukhada.hss@itbhu.ac.in, sukhada8@gmail.com
# To run:  python3 make-usr-csv.py inp-utf8

import sys, os, re, argparse

argument_parser = argparse.ArgumentParser(description = 'USR-CSV Creation Tool')
argument_parser.add_argument('input_file', type = str, help = 'File containing the input sentence in Devanagari with groups separated by parentheses')
argument_parser.add_argument('--edit', default = False, action = 'store_true', help = 'If specified, runs the USR-CSV Creation TUI, else builds a USR-CSV file with the values selected by default')

input_file = argument_parser.parse_args().input_file
edit_mode = argument_parser.parse_args().edit

if edit_mode:

	import urwid

	class UsrCreationTUI(urwid.WidgetWrap):

		palette = [
			('body',         'black',        'light gray', 'standout'),
			('screen edge',  'light blue',   'dark cyan'),
			('main shadow',  'dark gray',    'black'),
			('line',         'black',        'light gray', 'standout'),
			('bg background','light gray',   'black'),
			('bg 1',         'black',        'dark blue', 'standout'),
			('bg 1 smooth',  'dark blue',    'black'),
			('bg 2',         'black',        'dark cyan', 'standout'),
			('bg 2 smooth',  'dark cyan',    'black'),
			('button normal','light gray',   'dark blue', 'standout'),
			('button select','white',        'dark green'),
			('line',         'black',        'light gray', 'standout'),
			('pg normal',    'white',        'black', 'standout'),
			('pg complete',  'white',        'dark magenta'),
			('pg smooth',    'dark magenta', 'black')
		]

		def __init__(self, titleList, optionViewsTitlesList, optionsList, optionsSelectedList):
			# These are references to the original lists and can therefore change the original lists
			self.titleList = titleList
			self.optionViewsTitlesList = optionViewsTitlesList
			self.optionsList = optionsList
			self.optionsSelectedList = optionsSelectedList
			urwid.WidgetWrap.__init__(self, self.main_window())

		def on_mode_button(self, button, state, button_data):
			"""Notify the controller of a new mode setting."""
			index = button_data[0]
			viewIndex = button_data[1]
			optionNum = button_data[2]
			if state:
				self.optionsSelectedList[index][viewIndex] = optionNum

		def main_shadow(self, w):
			"""Wrap a shadow and background around widget w."""
			bg = urwid.AttrWrap(urwid.SolidFill(u"\u2592"), 'screen edge')
			shadow = urwid.AttrWrap(urwid.SolidFill(u" "), 'main shadow')

			bg = urwid.Overlay( shadow, bg,
				('fixed left', 3), ('fixed right', 1),
				('fixed top', 2), ('fixed bottom', 1))
			w = urwid.Overlay( w, bg,
				('fixed left', 2), ('fixed right', 3),
				('fixed top', 1), ('fixed bottom', 2))
			return w

		def button(self, t, fn):
			w = urwid.Button(t, fn)
			w = urwid.AttrWrap(w, 'button normal', 'button select')
			w = urwid.Padding(w, left=4, right=4)
			return w

		def radio_button(self, g, index, viewIndex, l, fn):
			w = urwid.RadioButton(g, 
				str(self.optionsList[index][viewIndex][l]),
				l == self.optionsSelectedList[index][viewIndex], 
				on_state_change = fn,
				user_data = (index, viewIndex, l))
			w = urwid.AttrWrap(w, 'button normal', 'button select')
			return w

		def exit_window(self, w):
			raise urwid.ExitMainLoop()

		def skip_TUI(self, w):
			global edit_mode
			edit_mode = False
			self.exit_window(w)

		def options_controls(self, optionsSubsetIndex, viewIndex):
			# setup mode radio buttons
			self.mode_buttons = []
			group = []
			if self.optionsList[optionsSubsetIndex][viewIndex]:
				for m in range(len(self.optionsList[optionsSubsetIndex][viewIndex])):
					rb = self.radio_button(group, optionsSubsetIndex, viewIndex, m, self.on_mode_button)
					self.mode_buttons.append(rb)
			else:
				rb = urwid.RadioButton(group, 'No Options Available', True)
				rb = urwid.AttrWrap(rb, 'button normal', 'button select')
				self.mode_buttons.append(rb)

			l = [urwid.Text(self.optionViewsTitlesList[optionsSubsetIndex][viewIndex], align="center"),
				] + self.mode_buttons
			w = urwid.ListBox(urwid.SimpleListWalker(l))
			return w

		def main_window(self):
			vline = urwid.AttrWrap( urwid.SolidFill(u'\u2502'), 'line')
			hline = urwid.AttrWrap( urwid.SolidFill(u'\u2500'), 'line')
			pile = [
				('pack', urwid.Text("USR-CSV Creation Tool", align="center")),
				('fixed', 1, hline)
			]
			for index in range(len(self.titleList)):
				optionViews = [self.options_controls(index, 0)]
				for viewIndex in range(1, len(self.optionViewsTitlesList[index])):
					optionViews.extend([
						('fixed', 1, vline),
						self.options_controls(index, viewIndex)
					])
				pile.extend([
					('pack', urwid.Text(self.titleList[index], align="center")),
					('fixed', 1, hline),
					urwid.Columns(optionViews, dividechars=1),
					('fixed', 1, hline)
				])
			pile.extend([
				('flow', self.button("Continue", self.exit_window)),
				('flow', self.button("Skip", self.skip_TUI))
			])
			w = urwid.Pile(pile)
			w = urwid.Padding(w,('fixed left',1),('fixed right',0))
			w = urwid.AttrWrap(w,'body')
			w = urwid.LineBox(w)
			w = urwid.AttrWrap(w,'line')
			w = self.main_shadow(w)
			return w
		
		def main(self):
			self.loop = urwid.MainLoop(self, self.palette)
			self.loop.run()

with open(input_file, 'r') as f: #Input: (लडका) (बगीचे में) (नयी किताब) (पढ रहा है) (.)
	sent = f.read()
myfw = input_file + '_USR.csv'

mySent = ''
for g in filter(None, re.split('^\s*\(\s*|\s*\)\s*\(\s*|\s*\)\s*$', sent)):
	myWrds = g.split()
	mySent += ' ' + ' '.join(myWrds)

with open('myinp.utf8', 'w') as fwS:
	fwS.write(mySent.strip())

# Running commands to parse the input
os.system('isc-parser -i myinp.utf8 > myinp.parse')
os.system('utf8_wx myinp.parse > myinp.parse.wx')
os.system(f'utf8_wx {input_file} > myinp.wx')

fwUSRcsv = open(myfw, 'w') 

# Row1
fwUSRcsv.write('#' + sent)

with open('myinp.wx', 'r') as inpWX:
	sentWX = inpWX.read()

myGrps = []
grpDict = {}
grpNum = 0
for g in filter(None, re.split('^\s*\(\s*|\s*\)\s*\(\s*|\s*\)\s*$', sentWX)):
	myGrps.append(g)
	grpNum += 1
	lst = g.split()
	for word in lst:
		grpDict[word] = grpNum

with open('myinp.parse.wx', 'r') as f1:
	parse = f1.readlines()
myParse = []
for line in parse:   # Ommiting empty lines from Deep Hindi Parse output
	if line.strip() != '':
		myParse.append(line)


# Getting TAM info
tamDict = {}
mytam = ''
with open('TAM-num-per-details.tsv.wx') as TAM_file:
	for line in TAM_file:
		line = line.strip()
		if line:    # cleaning TAM to match it with the input
			tam_features = line.split('\t')
			tam = list(set(tam_features[2:]))
			mytam = tam_features[1]
			if tam != []: 
				if '' in tam:
					tam.remove('')
				tamDict[mytam] = tam 

tamOptions = []
tamOptionsSelected = [] # Selecting the largest TAM initially from multiple TAMs for the same group
for grp in myGrps:
	tamBest = ''
	tamLst = []
	for k in tamDict.keys():
		for t in tamDict[k]:
			if grp.endswith(t): # Matching TAM with input chunks
				tamLst.append(k)
	tamOptions.append(tamLst)
	bestTamIndex = 0
	for i in range(1, len(tamLst)):
		if len(tamLst[i]) > len(tamLst[bestTamIndex]):
			bestTamIndex = i
	if not edit_mode:
		if len(tamLst) > 1:
			print(grp, ': Other possible TAM/s:')
			for i in range(len(tamLst)):
				if i != bestTamIndex:
					print('\t', tamLst[i])
	tamOptionsSelected.append(bestTamIndex)

if edit_mode:
	UsrCreationTUI(['TAM Options'], [myGrps], [tamOptions], [tamOptionsSelected]).main()

def getSelectedTAM(grp_index):
	if tamOptions[grp_index]:
		return('-' + tamOptions[grp_index][tamOptionsSelected[grp_index]])
	else:
		return('')

def morph(wrd):
	with open('myword.txt', 'w') as fw:
		fw.write(wrd)
		fw.write('\n')
	cmd = 'lt-proc -c -a new_hnd_mo/hi.morf.bin myword.txt > mymorph.txt'
	os.system(cmd)
	with open('mymorph.txt', 'r') as f:
		morf = f.read().strip()[:-1].split('/')
	return(morf)

def RCCGN(morf):
	rut = morf[1].split('<')
	return(rut)

vibList = ['awIwa', 'aMxara', 'Upara', 'kA', 'kI', 'kI ora', 'ke', 'ke awirikwa', 'ke bAxa', 'ke bAxa se', 'ke bAre meM', 'ke bAvajUxa', 'ke bIca', 'ke bIca meM', 'ke mAXyama se', 'ke lie', 'ke viroXa', 'ke viRaya meM', 'ko', 'ko CodZakara', 'cAroM ora', 'CodZakara', 'jaba waka', 'jEsA', 'waka', 'waba waka', 'waba se', 'xOrAna', 'xvArA', 'nA', 'nikata', 'nimnaliKiwa', 'nIce', 'ne', 'para', 'para vicAra', 'pare', 'pAra', 'pICe', 'bagala meM', 'baMxa', 'banAma', 'bAhara', 'binA', 'Binna', 'meM ', 'lekina', 'viparIwa', 'viroXI', 'samaya', 'sAWa', 'sAWa meM', 'sAmane', 'sivAya', 'se', 'se pahale']

startCount = 0
endCount = 0
row2 = []
for g_index in range(len(myGrps)):
	startCount = endCount
	endCount = startCount + len(myGrps[g_index].split())
	cntntWrds = [] 
	chnk = ''
	for i in range(startCount, endCount):
		cat = myParse[i].split()[3] 
		if len(myGrps[g_index].split()) <= 1:
			if cat != 'VM' and cat != 'SYM':
				chnk = RCCGN(morph(myGrps[g_index]))[0]
				chnk = chnk + '_0'
			elif cat == 'VAUX':
				pass
			elif cat == 'VM': 
				chnk = RCCGN(morph(myGrps[g_index]))[0]
				chnk = chnk + getSelectedTAM(g_index) 
			elif cat == 'SYM':
				chnk = myGrps[g_index]
		else:
			morf = RCCGN(morph(myParse[i].split()[2]))
			if cat == 'JJ':
				chnk = chnk + morf[0] + '~'
			if cat == 'QC':
				chnk = chnk + morf[0] + '@'
			elif cat == 'PSP':
				chnk = chnk + '_' + myParse[i].split()[1] 
			elif cat == 'VAUX':
				pass
			elif cat == 'VM':
				chnk = RCCGN(morph(myGrps[g_index]))[0]
				chnk = chnk + getSelectedTAM(g_index) 
			else:
				if i == endCount-1 and cat != 'PSP':
					chnk = chnk + morf[0] + '_0' 
				else: 
					chnk = chnk + morf[0] 
	row2.append(chnk)

myrow2 = '#' + ','.join(row2) + '\n'
fwUSRcsv.write(myrow2)

# Getting row3 info
# Generating Hindi concept info
HinConcepts = {}
for i in open('H_concept-to-mrs-rels.dat'):
	if i.strip() != '':    # looking for non-empty lines
		con = i.split()[1].split('_')[0]
		if con not in HinConcepts.keys():
			HinConcepts[con] = [i.split()[1:]]
		else:
			cons = HinConcepts[con]
			cons.append(i.split()[1:])

def getHinConcept(word):
	morf = RCCGN(morph(word))
	if morf[0] in HinConcepts.keys():
		return(HinConcepts[morf[0]])
	else:
		print('WARNING: "', word,'" not found in the Hindi concept dictionary')
		return(word)

all_words = []
hinConceptOptions = []
hinConceptOptionsSelected = []

startCount = 0
endCount = 0
row3 = []
lst = ['lwg__psp', 'rsym', 'lwg__vaux', 'lwg__vaux_cont']
for g in myGrps:
	startCount = endCount
	endCount = startCount + len(g.split())
	conceptWrds = [] 
	for i in range(startCount, endCount):
		parseline = myParse[i].split()
		all_words.append(parseline[2])
		if parseline[7] in lst: 
			hinConceptOptions.append([])
		else:
			myconcept = getHinConcept(parseline[2])
			if type(myconcept) == list:
				conceptOptions = []
				for concept in myconcept:
					conceptOptions.append(concept)
				hinConceptOptions.append(conceptOptions)
			else:
				hinConceptOptions.append([[myconcept]])
		hinConceptOptionsSelected.append(0)

if edit_mode:
	UsrCreationTUI(["Hindi Concept Options"], [all_words], [hinConceptOptions], [hinConceptOptionsSelected]).main()

startCount = 0
endCount = 0
row3 = []
for g_index in range(len(myGrps)):
	startCount = endCount
	endCount = startCount + len(myGrps[g_index].split())
	conceptWrds = [] 
	for i in range(startCount, endCount):
		parseline = myParse[i].split()
		if parseline[7] in lst: 
			pass
		else:
			myconcept = hinConceptOptions[i][hinConceptOptionsSelected[i]][0]
			morf = RCCGN(morph(parseline[2]))
			if morf[0] in HinConcepts.keys():
				if parseline[3] == 'JJ': 
					concept = myconcept + '~'
					conceptWrds.append(concept)
				elif parseline[3] == 'QC': 
					concept = myconcept + '@'
					conceptWrds.append(concept)
				elif parseline[3] == 'VM':
					concept = myconcept + getSelectedTAM(g_index)
					conceptWrds.append(concept)
				else:
					conceptWrds.append(myconcept)
			else:
				concept = morf[0] + getSelectedTAM(g_index)
				conceptWrds.append(concept)
			if not edit_mode and len(getHinConcept(morf[0])) > 1 and type(getHinConcept(morf[0])) == list:
				print(parseline[1], ': Other possible Hindi concept/s:')
				all_concepts = HinConcepts[morf[0]]
				for cncpt_index in range(1, len(all_concepts)):
					print('\t', all_concepts[cncpt_index])

	if conceptWrds != []:
		row3.append(conceptWrds)
ROW3 = ''
for c in row3:
	ROW3 = ROW3 + ''.join(c) + ','
myrow3 = ROW3[:-1] + '\n'
fwUSRcsv.write(myrow3)

# Computing row4 info
row4 = []
for i in range(1,len(row3)+1):
	row4.append(str(i))

myrow4 = ','.join(row4) + '\n'
fwUSRcsv.write(myrow4)


row5Options = []
row5OptionsSelected = []

grpRow5Options = ['pron', 'propn', 'def', 'mass']

row5Map = {}
for i in range(len(grpRow5Options)):
	row5Map[grpRow5Options[i]] = i

# Computing row5 info
startCount = 0
endCount = 0
lst = ['JJ', 'PSP', 'VM', 'VAUX', 'SYM', '.', '?']
for g in myGrps:
	startCount = endCount
	endCount = startCount + len(g.split())
	row5Option = None
	for i in range(startCount, endCount):
		cat = myParse[i].split()[3]
		if cat in lst:
			pass
		else:
			if cat == 'PRP':
				row5Option = row5Map['pron']
			elif cat == 'NN':
				row5Option = row5Map['def']
			elif cat == 'NNP':
				row5Option = row5Map['propn']
		if row5Option == None:
			row5Options.append([])
			row5OptionsSelected.append(0)
		else:
			row5Options.append(grpRow5Options)
			row5OptionsSelected.append(row5Option)

if edit_mode:
	UsrCreationTUI(['Row 5 Options'], [myGrps], [row5Options], [row5OptionsSelected]).main()

row5 = ''
for g_index in range(len(myGrps)):
	if row5Options[g_index]:
		row5 += row5Options[g_index][row5OptionsSelected[g_index]]
	row5 += ','

myrow5 = row5 + '\n'
fwUSRcsv.write(myrow5)

genderOptions = []
genderOptionsSelected = []
numberOptions = []
numberOptionsSelected = []
personOptions = []
personOptionsSelected = []

grpGenderOptions = ['-', 'm', 'f']
grpNumberOptions = ['-', 'sg', 'pl']
grpPersonOptions = ['-', 'u', 'm', 'a']
genderMap = {}
numberMap = {}
personMap = {}
for i in range(len(grpGenderOptions)):
	genderMap[grpGenderOptions[i]] = i
for i in range(len(grpNumberOptions)):
	numberMap[grpNumberOptions[i]] = i
for i in range(len(grpPersonOptions)):
	personMap[grpPersonOptions[i]] = i

# Computing row6 (GNP) info
startCount = 0
endCount = 0
row6 = ''
lst = ['JJ', 'PSP', 'VM', 'VAUX', 'SYM', '.', '?']
for g in myGrps:
	startCount = endCount
	endCount = startCount + len(g.split())
	mygnp = ''
	grpGenderSelected = 0
	grpNumberSelected = 0
	grpPersonSelected = 0
	foundInformation = False
	for i in range(startCount, endCount):
		cat = myParse[i].split()[3]
		wrd = myParse[i].split()[1]
		if cat in lst:
			pass
		else:
			if cat == 'PRP' or cat == 'NN':
				morf = morph(wrd)
				for m in morf[1:]:
					gnp = m.split('<')
					g = gnp[-3].split(':')[1][:-1]
					n = gnp[-2].split(':')[1]
					p = gnp[-1].split(':')[1][:-1]
					if 'cat:p>' in gnp and cat == 'PRP':
						if n == 's>':
							# mygnp = '[' + g + ' sg ' + p + ']'
							grpNumberSelected = numberMap['sg']
						else:
							# mygnp = '[' + g + ' pl ' + p + ']'
							grpNumberSelected = numberMap['pl']
						grpGenderSelected = genderMap[g]
						grpPersonSelected = personMap[p]
					else:
						if 'cat:n>' in gnp:
							if n == 'num:s':
								# mygnp = '[- sg -]'
								grpNumberSelected = numberMap['sg']
							else:
								# mygnp = '[- pl -]'
								grpNumberSelected = numberMap['pl']
						grpGenderSelected = genderMap['-']
						grpPersonSelected = personMap['-']
				# gnp = mygnp
				foundInformation = True
				break
	if foundInformation:
		genderOptions.append(grpGenderOptions)
		numberOptions.append(grpNumberOptions)
		personOptions.append(grpPersonOptions)
	else:
		genderOptions.append([])
		numberOptions.append([])
		personOptions.append([])
	genderOptionsSelected.append(grpGenderSelected)
	numberOptionsSelected.append(grpNumberSelected)
	personOptionsSelected.append(grpPersonSelected)
	# if mygnp == '' : 
	# 	pass 
	# else:
	# 	row6 = row6 + mygnp + ','

if edit_mode:
	UsrCreationTUI(
		['Gender Options', 'Number Options', 'Person Options'],
		[myGrps, myGrps, myGrps],
		[genderOptions, numberOptions, personOptions],
		[genderOptionsSelected, numberOptionsSelected, personOptionsSelected]
	).main()

for g_index in range(len(myGrps)):
	if genderOptions[g_index]: # Empty if not a Noun or Pronoun Clause
		row6 += f'[{grpGenderOptions[genderOptionsSelected[g_index]]} {grpNumberOptions[numberOptionsSelected[g_index]]} {grpPersonOptions[personOptionsSelected[g_index]]}]'
		row6 += ','

myrow6 = row6 + '\n'
fwUSRcsv.write(myrow6)


intraChunkRelationsOptions = []
intraChunkRelationsOptionsSelected = []
intraChunkHeadOptions = []
intraChunkHeadOptionsSelected = []
intraChunkDependentOptions = []
intraChunkDependentOptionsSelected = []
interChunkRelationsOptions = []
interChunkRelationsOptionsSelected = []
interChunkHeadOptions = []
interChunkHeadOptionsSelected = []

grpIntraChunkRelationsOptions = ['Not Applicable', 'viSeRaNa', 'viSeRya-viSeRaNa', 'saMKyA-viSeRaNa']
grpInterChunkRelationsOptions = ['Not Applicable', 'k1', 'k2', 'k3', 'k4', 'k5', 'r6', 'k7', 'k7p']

intraChunkRelationsMap = {}
interChunkRelationsMap = {}
for i in range(len(grpIntraChunkRelationsOptions)):
	intraChunkRelationsMap[grpIntraChunkRelationsOptions[i]] = i
for i in range(len(grpInterChunkRelationsOptions)):
	interChunkRelationsMap[grpInterChunkRelationsOptions[i]] = i

# Computing row7 and row8, intra-chunk and inter-chunk relation
c = 0
lst = ['lwg__psp', 'rsym', 'lwg__vaux', 'main', 'lwg__vaux_cont']
relMap = {'nmod__adj': 'viSeRaNa'}
startCount = 0
endCount = 0
for g in myGrps:
	startCount = endCount
	endCount = startCount + len(g.split())
	intra = intraChunkRelationsMap['Not Applicable']
	inter = interChunkRelationsMap['Not Applicable']
	interHead = len(myGrps) - 2
	c += 1
	for i in range(startCount, endCount):
		rel = myParse[i].split()[6:8]
		cat = myParse[i].split()[3]
		lhs_wrd = myParse[int(rel[0])-1].split()[1]
		if rel[1] in lst: 
			pass
		else:
			if rel[1].startswith('k'):
				inter = interChunkRelationsMap[rel[1]]
				interHead = grpDict[lhs_wrd] - 1
			else:
				if cat == 'QC': 
					intra = intraChunkRelationsMap['saMKyA-viSeRaNa']
				else:
					intra = intraChunkRelationsMap['viSeRaNa']
	if intra == intraChunkRelationsMap['Not Applicable']:
		intraChunkRelationsOptions.append([])
		intraChunkRelationsOptionsSelected.append(0)
		intraChunkHeadOptions.append([])
		intraChunkHeadOptionsSelected.append(0)
		intraChunkDependentOptions.append([])
		intraChunkDependentOptionsSelected.append(0)
	else:
		intraChunkRelationsOptions.append(grpIntraChunkRelationsOptions)
		intraChunkRelationsOptionsSelected.append(intra)
		intraChunkHeadOptions.append(g.split())
		intraChunkHeadOptionsSelected.append(0)
		intraChunkDependentOptions.append(g.split())
		intraChunkDependentOptionsSelected.append(0)
	if inter == interChunkRelationsMap['Not Applicable']:
		interChunkRelationsOptions.append([])
		interChunkRelationsOptionsSelected.append(0)
		interChunkHeadOptions.append([])
		interChunkHeadOptionsSelected.append(0)
	else:
		interChunkRelationsOptions.append(grpInterChunkRelationsOptions)
		interChunkRelationsOptionsSelected.append(inter)
		interChunkHeadOptions.append(myGrps[:-1])
		interChunkHeadOptionsSelected.append(interHead)

if edit_mode:
	UsrCreationTUI(
		['Intra Chunk Relations Options', 'Head Options', 'Dependent Options'],
		[myGrps, myGrps, myGrps],
		[intraChunkRelationsOptions, intraChunkHeadOptions, intraChunkDependentOptions],
		[intraChunkRelationsOptionsSelected, intraChunkHeadOptionsSelected, intraChunkDependentOptionsSelected]
	).main()
	UsrCreationTUI(
		['Inter Chunk Relations Options', 'Head Options'],
		[myGrps, myGrps],
		[interChunkRelationsOptions, interChunkHeadOptions],
		[interChunkRelationsOptionsSelected, interChunkHeadOptionsSelected]
	).main()

row7 = ''
row8 = ''
for g_index in range(len(myGrps)):
	if intraChunkRelationsOptionsSelected[g_index] != intraChunkRelationsMap['Not Applicable']:
		row7 += str(g_index + 1) + '.' + str(intraChunkDependentOptionsSelected[g_index] + 1) + ':' + intraChunkRelationsOptions[g_index][intraChunkRelationsOptionsSelected[g_index]] \
		+ '~' + str(g_index + 1) + '.' + str(intraChunkHeadOptionsSelected[g_index] + 1) + ':' + intraChunkRelationsOptions[g_index][intraChunkRelationsOptionsSelected[g_index]]
	if interChunkRelationsOptionsSelected[g_index] != interChunkRelationsMap['Not Applicable']:
		row8 += str(interChunkHeadOptionsSelected[g_index] + 1) + ':' + interChunkRelationsOptions[g_index][interChunkRelationsOptionsSelected[g_index]]
	if g_index < len(myGrps) - 2:
		row7 += ','
		row8 += ','

myrow7 = row7 + '\n'
myrow8 = row8 + '\n'
fwUSRcsv.write(myrow7)
fwUSRcsv.write(myrow8)

myrow9 = ',' * (len(myGrps)-2) + '\n'
fwUSRcsv.write(myrow9)


sentenceTypeOptions = [['assertive', 'negative', 'imperative', 'question']]
sentenceTypeOptionsSelected = [0]

sentenceTypeMap = {}
for i in range(len(sentenceTypeOptions[0])):
	sentenceTypeMap[sentenceTypeOptions[0][i]] = i

# row10
if 'rsym' in myParse[-1]:
	if myParse[-2].split()[1] == '.' and 'nahIM' in mySent: 
		sentenceTypeOptionsSelected[0] = sentenceTypeMap['negative']
	elif '-' in myrow2 and myParse[-2].split()[1] == '.' and (myrow2.split('-')[1].startswith('o_1') or myrow2.split('-')[1].startswith('ie_1') ):
		sentenceTypeOptionsSelected[0] = sentenceTypeMap['imperative']
	elif myParse[-2].split()[1] == '?':
		sentenceTypeOptionsSelected[0] = sentenceTypeMap['question']
	else:
		sentenceTypeOptionsSelected[0] = sentenceTypeMap['assertive']

wholeSentence = mySent.strip()
if edit_mode:
	UsrCreationTUI(['Sentence Type Options'], [[wholeSentence]], [sentenceTypeOptions], [sentenceTypeOptionsSelected]).main()

sentType = sentenceTypeOptions[0][sentenceTypeOptionsSelected[0]]
fwUSRcsv.write(sentType + '\n')
fwUSRcsv.close()

if '-' not in myrow2:
	print(myrow2, '\nNo TAM found in the sentence')

print('----------------------------------------------------')
catfile = 'cat ' + myfw
os.system(catfile)
print('----------------------------------------------------\nThe output file is:', myfw)
