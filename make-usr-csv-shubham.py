#!/usr/bin/python3

# Written by Sukhada. Email: sukhada.hss@itbhu.ac.in, sukhada8@gmail.com
#To run:  python3 make-usr-csv.py inp-utf8

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
			('body',         'black',      'light gray', 'standout'),
			('screen edge',  'light blue', 'dark cyan'),
			('main shadow',  'dark gray',  'black'),
			('line',         'black',      'light gray', 'standout'),
			('bg background','light gray', 'black'),
			('bg 1',         'black',      'dark blue', 'standout'),
			('bg 1 smooth',  'dark blue',  'black'),
			('bg 2',         'black',      'dark cyan', 'standout'),
			('bg 2 smooth',  'dark cyan',  'black'),
			('button normal','light gray', 'dark blue', 'standout'),
			('button select','white',      'dark green'),
			('line',         'black',      'light gray', 'standout'),
			('pg normal',    'white',      'black', 'standout'),
			('pg complete',  'white',      'dark magenta'),
			('pg smooth',     'dark magenta','black')
			]

		def __init__(self, title, OptionViewsTitles, Options, OptionsSelected):
			# These are references to the original lists and can therefore change the original lists
			self.title = title
			self.OptionViewsTitles = OptionViewsTitles
			self.Options = Options
			self.OptionsSelected = OptionsSelected
			urwid.WidgetWrap.__init__(self, self.main_window())

		def on_mode_button(self, button, state, button_data):
			"""Notify the controller of a new mode setting."""
			if state:
				self.OptionsSelected[button_data[0]] = button_data[1]

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
			return w

		def radio_button(self, g, viewIndex, l, fn):
			w = urwid.RadioButton(g, 
				str(self.Options[viewIndex][l]),
				l == self.OptionsSelected[viewIndex], 
				on_state_change = fn,
				user_data = (viewIndex, l))
			w = urwid.AttrWrap(w, 'button normal', 'button select')
			return w

		def exit_program(self, w):
			raise urwid.ExitMainLoop()

		def options_controls(self, viewIndex):
			# setup mode radio buttons
			self.mode_buttons = []
			group = []
			if self.Options[viewIndex]:
				for m in range(len(self.Options[viewIndex])):
					rb = self.radio_button( group, viewIndex, m, self.on_mode_button )
					self.mode_buttons.append( rb )
			else:
				rb = urwid.RadioButton(group, 'No Options Available', True)
				rb = urwid.AttrWrap(rb, 'button normal', 'button select')
				self.mode_buttons.append( rb )

			l = [urwid.Text(self.OptionViewsTitles[viewIndex], align="center"),
				] + self.mode_buttons
			w = urwid.ListBox(urwid.SimpleListWalker(l))
			return w

		def main_window(self):
			vline = urwid.AttrWrap( urwid.SolidFill(u'\u2502'), 'line')
			OptionViewsTitlesList = [self.options_controls(0)]
			for viewIndex in range(1, len(self.OptionViewsTitles)):
				OptionViewsTitlesList.append(('fixed',1,vline))
				OptionViewsTitlesList.append(self.options_controls(viewIndex))
			w = urwid.Columns(OptionViewsTitlesList, dividechars=1, focus_column=2)
			hline = urwid.AttrWrap( urwid.SolidFill(u'\u2500'), 'line')
			w = urwid.Pile([
				('pack', urwid.Text("USR-CSV Creation Tool", align="center")),
				('fixed', 1, hline),
				('pack', urwid.Text(self.title, align="center")),
				('fixed', 1, hline),
				w,
				('fixed', 1, hline),
				('flow', self.button("Continue", self.exit_program ))])
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
# TODO: Think about the input representation
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
# print(grpDict)

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
# print(tamDict.keys())
# for key in tamDict.keys():
#     print(key)
#     print(tamDict[key])

tamOptions = []
tamOptionsSelected = [] # Selecting the largest TAM initially from multiple TAMs for the same group
for grp in myGrps:
	tamBest = ''
	tamLst = []
	for k in tamDict.keys():
		for t in tamDict[k]:
			# TODO: Understand this
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

# print(myGrps)
# print(tamOptions)
# print(tamOptionsSelected)

if edit_mode:
	UsrCreationTUI('TAM Options', myGrps, tamOptions, tamOptionsSelected).main()

# print(tamOptionsSelected)

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

# print(morph('Upara'))

def RCCGN(morf):
	rut = morf[1].split('<')
	return(rut)

#print(RCCGN(morph('ladakiyoM')))

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
		if len(g.split()) <= 1:
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

#print(HinConcepts['A'])

def getHinConcept(word):
	morf = RCCGN(morph(word))
	if morf[0] in HinConcepts.keys():
		return(HinConcepts[morf[0]])
	else:
		print('WARNING: "', word,'" not found in the Hindi concept dictionary')
		return(word)

#print(getHinConcept('A'))
#print(getHinConcept('mEM'))

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

# print(all_words)
# print(hinConceptOptions)
# print(hinConceptOptionsSelected)

if edit_mode:
	UsrCreationTUI("Hindi Concept Options", all_words, hinConceptOptions, hinConceptOptionsSelected).main()

# print(hinConceptOptionsSelected)

startCount = 0
endCount = 0
row3 = []
for g in myGrps:
	startCount = endCount
	endCount = startCount + len(g.split())
	conceptWrds = [] 
	for i in range(startCount, endCount):
		parseline = myParse[i].split()
		if parseline[7] in lst: 
			pass
		else:
			# print(getHinConcept(parseline[2]))
			myconcept = hinConceptOptions[i][hinConceptOptionsSelected[i]][0]
			# print(myconcept)
			morf = RCCGN(morph(parseline[2]))
			# print(parseline)
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

# Computing row5 info
startCount = 0
endCount = 0
row5 = ''
for g in myGrps:
	startCount = endCount
	endCount = startCount + len(g.split())
	lst = ['JJ', 'PSP', 'VM', 'VAUX', 'SYM', '.', '?']
	r5 = ''
	for i in range(startCount, endCount):
		cat = myParse[i].split()[3]
		if cat in lst: 
			pass
		else:
			if cat == 'PRP':
				r5 = 'pron'
			elif cat == 'NN':
				r5 = 'def'
			elif cat == 'NNP':
				r5 = 'propn'
	if r5 == '' : 
		pass 
	else:
		row5 = row5 + r5 + ','
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
					n = gnp[-2].split(':')[1][:-1]
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
	UsrCreationTUI('Gender Options', myGrps, genderOptions, genderOptionsSelected).main()
	UsrCreationTUI('Number Options', myGrps, numberOptions, numberOptionsSelected).main()
	UsrCreationTUI('Person Options', myGrps, personOptions, personOptionsSelected).main()

for g_index in range(len(myGrps)):
	if genderOptions[g_index]: # Empty if not a Noun or Pronoun Clause
		row6 += f'[{grpGenderOptions[genderOptionsSelected[g_index]]} {grpNumberOptions[numberOptionsSelected[g_index]]} {grpPersonOptions[personOptionsSelected[g_index]]}]'
		row6 += ','

myrow6 = row6 + '\n'
fwUSRcsv.write(myrow6)

# Computing row7 and row8, intra-chunk and inter-chunk relation
startCount = 0
endCount = 0
row7 = []
row8 = []
c = 0
lst = ['lwg__psp', 'rsym', 'lwg__vaux', 'main', 'lwg__vaux_cont']
relMap = {'nmod__adj': 'viSeRaNa'}
for g in myGrps:
	startCount = endCount
	endCount = startCount + len(g.split())
	intra = ''
	inter = ''
	c += 1
	for i in range(startCount, endCount):
		rel = myParse[i].split()[6:8]
		cat = myParse[i].split()[3]
		lhs_wrd = myParse[int(rel[0])-1].split()[1]
		if rel[1] in lst: 
			pass
		else:
			if rel[1].startswith('k'):
				inter = str(grpDict[lhs_wrd]) + ':' + rel[1] 
			else:
				if cat == 'QC': 
					intra = str(c) + '.' + str(len(g.split())) + ':saMKyA-viSeRaNa'
				else:
					intra = str(c) + '.' + str(len(g.split())) + ':' + relMap[rel[1]]
		if inter != '':
			row8.append(inter)
			row7.append(',')
			break
		if intra != '':
			row7.append(intra)

myrow7 = ''.join(row7) + '\n'
myrow8 = ','.join(row8) + ',\n'
fwUSRcsv.write(myrow7)
fwUSRcsv.write(myrow8)

myrow9 = ',' * (len(myGrps)-2) + '\n'
fwUSRcsv.write(myrow9)

# row10
sentType = ''
if 'rsym' in myParse[-1]:
	if myParse[-2].split()[1] == '.' and 'nahIM' in mySent: 
		sentType = 'negative\n'
	elif '-' in myrow2 and myParse[-2].split()[1] == '.' and (myrow2.split('-')[1].startswith('o_1') or myrow2.split('-')[1].startswith('ie_1') ):
		sentType = 'imperative\n'
	elif myParse[-2].split()[1] == '?':
		sentType = 'question\n'
	else:
		sentType = 'assertive\n'

fwUSRcsv.write(sentType)
fwUSRcsv.close()

if '-' not in myrow2:
	print(myrow2, '\nNo TAM found in the sentence')

print('----------------------------------------------------')
catfile = 'cat ' + myfw
os.system(catfile)
print('----------------------------------------------------\nThe output file is:', myfw)
