#!/usr/bin/python3.6
# automation.py

# Base packages for standard window.
from requests import Session
from bs4 import BeautifulSoup as bs
import PySimpleGUI as psg # Specify specific components needed from PySimpleGUI

# NEED THIS TO IGNORE SSL CERTIFICATION ERROR.
# Security risk, but known source and known data, so it is fine.
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# loads for turning JSON into dictionary
# dumps for pretty printing
from json import loads, dumps

# Setting default font of all psg windows.
psg.set_options(font=("Helvetica", 14))

# TODO: Provide information context for this HEADERS variable.
HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.54'
}


def getFavaTestsuiteData(username: str, password: str, number: str) -> list:
    """Using the login information and testsuite number, loads the page, grabs the CSRF token, logs in using
    the provided account information, gets the testsuite list data, and finally returns that list.

    Args:
        username (str): Provided username from loginWindow().
        password (str): Provided password from loginWindow().
        number (str): Provided QMF number from loginWindow().

    Returns:
        list: A list of all of the Fava testsuite data from the given QMF machine number.
    """
    
    loginURL = "https://qmf{number}.fava.fb.com/login".format(number=number)
    
    payload = {
        'username': username,
        'password': password
    }
    
    with Session() as s:
        # TODO: Explain this.
        loginResponse = s.get(loginURL, headers=HEADERS, verify=False)
        soup = bs(loginResponse.text, 'html.parser')
        csrfToken = soup.find('input', {'id':'csrf_token'})['value']
        
        payload['csrf_token'] = csrfToken
        
        # TODO: Explain this.
        # Login - ...
        loginRequest = s.post(loginURL, data=payload, headers=HEADERS, verify=False)
        
        # Link returning the testsuite list data from the particular QMF machine (needs authentication, hence the need to login).
        testsuiteResponse = s.get("https://qmf{number}.fava.fb.com/testsuite/list?ans=1".format(number=number))
        return testsuiteResponse.json()['data']
        

def getFavaEngineConfig(number: str) -> str:
    """Gets the Fava Engine config automatically.

    Args:
        number (str): Machine number from the login prompt.

    Returns:
        str: Fava Engine config text.
    """
    
    favaEngineConfigURL = "https://qmf{number}.fava.fb.com/fava_engine".format(number=number)
    
    with Session() as s:
        response = s.get(favaEngineConfigURL, headers=HEADERS, verify=False)
        soup = bs(response.text, 'html.parser')
        favaEngineConfig = soup.find('pre').contents
        # favaEngineConfig is a list of strings
        return ''.join(favaEngineConfig)


def listToNameTagsDict(testsuiteList: list) -> dict:
    """Using the Fava testsuite list data, creates a dictionary (nameTagsDict) which is a dictionary with
    keys: name of the testsuite, values: release numbers of the testsuite, and finally returns the
    namesTagsDict.

    Args:
        testsuiteList (list): A QMF's Fava testsuite data.

    Returns:
        dict: The names of the testsuites with their associated release numbers.
    """
    
    nameTagsDict = {}
    for testsuite in testsuiteList:
        name = testsuite['name']
        tags = testsuite['tags']
        nameTagsDict[name] = tags
    
    return nameTagsDict


def getFavaConfigTestsuiteNames(favaEngineConfigJSON: dict) -> list:
    """Given the Fava Engine config in JSON format, iterates through the config and recognizes all instances of testsuite mappings.

    Args:
        favaEngineConfigJSON (dict): The Fava Engine config in JSON format.

    Returns:
        list: A list of all of the testsuite names extracted from the Fava Engine config.
    """
    
    testsuiteNames = []
    
    stageTestMap = favaEngineConfigJSON['stage_test_map']
    
    for device, testConfigs in stageTestMap.items():
        for test, testConfig in testConfigs.items():
            if type(testConfig) is str:
                if testConfig not in testsuiteNames:
                    testsuiteNames.append(testConfig)
            elif type(testConfig) is dict:
                if testConfig['testsuite'] not in testsuiteNames:
                    testsuiteNames.append(testConfig['testsuite'])
    
    return testsuiteNames


def getOnlyNameTagsWithReleaseDict(nameTagsDict: dict, release: str) -> list:
    """Given the nameTagsDict and the searched for release number, creates and returns a list of testsuites names whose tags contain the release.
    If no release is given ('') then returns the same nameTagsDict.

    Args:
        nameTagsDict (dict): Testsuites names with their associated tags (releases).
        release (str): The searched for release.

    Returns:
        list: Only the names of testsuites in nameTagsDict whose value (tags) contain the release.
    """
    
    testsuiteNamesContainedRelease = []

    # If user did not specify a release.
    if not release:
        for name in nameTagsDict.keys():
            testsuiteNamesContainedRelease.append(name)
    else:
        for name, tags in nameTagsDict.items():
            if release in tags:
                testsuiteNamesContainedRelease.append(name)
    
    return testsuiteNamesContainedRelease


def getFavaConfigTestsuiteNameMatchFavaTestsuiteData(nameTagsDict: dict, release: str, favaConfigTestsuiteNames: list) -> dict:
    # TODO: Finish Docstring on this function.
    """Given the dictionary of testsuite names and their associated tags (releases), the searched for release, and the matches found in the Fava engine 
    configuration, returns a dictionary of all testsuites with matches found in the favaEngineConfig with their associated values being the testsuites 
    whose names most closely match the testsuites found in the favaEngineConfig whose tags (releases) contain the searched for release number.

    Args:
        nameTagsDict (dict): Dictionary of all testsuite names and their associated tags (releases) of the particular QMF machine.
        release (str): The searched for release.
        matches (str): All testsuites found in the Fava engine configuration using iteration.

    Returns:
        dict: The testsuite names and their associated testsuites whose names most closely match their Fava engine configuration found counterpart and are also
                the searched for release.
    """
    
    testsuiteNameMatch = {}
    testsuiteNamesContainedRelease = getOnlyNameTagsWithReleaseDict(nameTagsDict, release)
    
    for testsuiteName in favaConfigTestsuiteNames:
        testsuiteNameMatch[testsuiteName] = set()
        currSearch = testsuiteName
        while currSearch != '' and not testsuiteNameMatch[testsuiteName]:
            for name in testsuiteNamesContainedRelease:
                if currSearch in name:
                    testsuiteNameMatch[testsuiteName].add(name)
            
            currSearch = currSearch[:-1]
    
    return testsuiteNameMatch


def getNewFavaConfigTestsuiteNames(favaEngineConfigJSON: dict, oldTestsuiteName: str, newTestsuiteName: str) -> dict:
    """Replaces the old testsuite name in the Fava Engine config JSON with the new testsuite name. and returns the new dict.

    Args:
        favaEngineConfigJSON (dict): Fava Engine config JSON.
        oldTestsuiteName (str): The old testsuite name to be replaced.
        newTestsuiteName (str): The new testsuite name to be the replacement.

    Returns:
        dict: The Fava Engine config with the new testsuite name replacing the old testsuite name.
    """
        
    for device, testConfigs in favaEngineConfigJSON['stage_test_map'].items():
        for test, testConfig in testConfigs.items():
            if type(testConfig) is str:
                if testConfig == oldTestsuiteName:
                    favaEngineConfigJSON['stage_test_map'][device][test] = newTestsuiteName
            elif type(testConfig) is dict:
                if testConfig['testsuite'] == oldTestsuiteName:
                    favaEngineConfigJSON['stage_test_map'][device][test]['testsuite'] = newTestsuiteName
    
    return favaEngineConfigJSON


def getLoginWindow() -> psg.Window:
    """Creates the layout of the login window and returns it. Used to login to the selected QMF machine.

    Returns:
        psg.Window: The login window.
    """
    
    # The login window layout
    loginLayout = [
        [psg.Text('Username: '), psg.InputText()],
        [psg.Text('Password: '), psg.InputText()],
        [psg.Text('QMF Number: '), psg.InputText()],
        [psg.Button('Login')]
    ]
    
    return psg.Window("Login", loginLayout, modal=True)


def getSearchWindow() -> psg.Window:
    """Creates the layout of the search window and returns it. Used to input/grab the Fava engine config text and output the found testsuite
    matches and also the final string with testsuite name version replacements.
    
    Returns:
        psg.Window: The search window.
    """
    
    # The search window layout.
    searchLayout = [
        [psg.Text('Fava Engine: '), psg.Button('Get Fava Engine Config')],
        [psg.Multiline(size=(60, 5), key='_favaEngineConfig')],
        [psg.Text('Release: '), psg.InputText(key='_release')],
        [psg.Button('Search')],
        [psg.Output(size=(60, 20), key='_output')]
    ]
    
    return psg.Window("Search", searchLayout, finalize=True)
    

def getReplacerWindow() -> psg.Window:
    """Creates the layout of the replacer window and returns it. Used to iterate over the matched testsuite names and the found names in the 
    testsuite list that contain the searched for release number. Buttons to iterate to skip the current testsuite search, replace it with
    the found matches, iterate over the found matches, and output the result string to the search window's output element.

    Returns:
        psg.Window: The replacer window.
    """
    
    # The replacer window layout.
    replacerLayout = [
        [psg.Text('Current testsuite search: ')],
        [psg.InputText(key='_search')],
        [psg.Text('Current testsuite match: ')],
        [psg.InputText(key='_match')],
        [psg.Text('Current testsuite matches: ')],
        [psg.Multiline(size=(60, 5), key='_matches')],
        [psg.Button('Start'), psg.Button('Skip', disabled=True), psg.Button('Replace', disabled=True), psg.Button('Next', disabled=True),
         psg.Button('Output', disabled=True)]
    ]
    
    return psg.Window('Replacer', replacerLayout, finalize=True)


# TODO: Can probably break up some of the processes in the replacerWindow functionality into functions
def _run() -> None:
    # TODO: Better explain what the _run() function does. And add some extra comment code to explain the process plus the meaning of button presses.
    """Runs the actual whole program.
    """
    
    # Start with the login window.
    # Starting with the login window will allow us to gain access to the testsuite list data.
    loginWindow = getLoginWindow()
    
    while True:
        event, values = loginWindow.read()
        if event == psg.WINDOW_CLOSED:
            break
        if event == 'Login':
            username = values[0].strip()
            password = values[1].strip()
            number = values[2].strip()
            # Using the login information call getFavaTestsuiteData() to grab the testsuite data.
            testsuiteData = getFavaTestsuiteData(username, password, number)
            break
    
    # Properly close the login window and set it to None as to not interfere with the multi-window in the later processes.
    loginWindow.close()
    loginWindow = None
    
    # Reorganize the testsuite data, which is a list of all testsuites, into a dictionary of testsuite names and their associated tags (releases).
    nameTagsDict = listToNameTagsDict(testsuiteData)
    
    # Start off with 1 window open by getting searchWindow and setting replacerWindow to None.
    searchWindow = getSearchWindow()
    replacerWindow = None
    
    while True:
        # The function read_all_windows() runs multiple windows.
        # The variable 'window' is the currently selected window.
        window, event, values = psg.read_all_windows()
        
        if event == psg.WINDOW_CLOSED:
            # Close the selected window.
            window.close()
            # Checks if the selected window is the replacer window or the search window.
            # If the replacerWindow is closed, the program still runs the search window.
            # If the searchWindow is closed, the program closes all windows and exits.
            if window == replacerWindow: # If closing replacerWindow, mark as closed.
                replacerWindow = None
            elif window == searchWindow: # If closing searchWindow, exit program.
                break
        
        if event == 'Get Fava Engine Config':
            searchWindow['_favaEngineConfig'].Update(getFavaEngineConfig(number))
            searchWindow['_output'].Update('')

        
        if event == 'Search':
            # Clears the output text window.
            searchWindow['_output'].Update('')
            
            # TODO: Clean up the values indexing and use keys instead.
            favaEngineConfig = searchWindow['_favaEngineConfig'].get()
            release = searchWindow['_release'].get()

            favaEngineConfigJSON = loads(favaEngineConfig)

            testsuiteNames = getFavaConfigTestsuiteNames(favaEngineConfigJSON)
            
            # TODO: Explain this.
            found = getFavaConfigTestsuiteNameMatchFavaTestsuiteData(nameTagsDict, release, testsuiteNames)
            
            # Prints the found testsuite names in the favaEngineConfig and the found name matches with the searched for release number set.
            for key, value in found.items():
                print(key, value)
            
            # Opens the replacerWindow.
            replacerWindow = getReplacerWindow()
            
            # After a search, refreshes the searchWindow so that the psg.Output element can be read by the user.
            searchWindow.refresh()
        
        # Start of the replacerWindow search.
        if event == 'Start':
            currTestsuite = 0
            replacerWindow['_search'].Update(testsuiteNames[currTestsuite])
            replacerWindow['_matches'].Update(found[testsuiteNames[currTestsuite]])
            currIter = iter(found[testsuiteNames[currTestsuite]])
            currMatch = next(currIter)
            replacerWindow['_match'].Update(str(currMatch))
            
            # Enable the buttons.
            replacerWindow['Skip'].update(disabled=False)
            replacerWindow['Replace'].update(disabled=False)
            replacerWindow['Next'].update(disabled=False)
            replacerWindow['Output'].update(disabled=False)

                    
        # Iterates to the next testsuite match in the testsuite matches.
        # Loops back around.
        if event == 'Next':
            try:
                currMatch = next(currIter)
            except StopIteration:
                currIter = iter(found[testsuiteNames[currTestsuite]])
                currMatch = next(currIter)
            finally:
                replacerWindow['_match'].Update(str(currMatch))
        
        # Skips the current testsuite match and goes to the next.
        if event == 'Skip':
            try:
                currTestsuite += 1
                replacerWindow['_search'].Update(str(testsuiteNames[currTestsuite]))
                replacerWindow['_matches'].Update(str(found[testsuiteNames[currTestsuite]]))
                currIter = iter(found[testsuiteNames[currTestsuite]])
                currMatch = next(currIter)
                replacerWindow['_match'].Update(str(currMatch))
            except (StopIteration, IndexError) as e:
                # Disable the buttons to prevent user error.
                replacerWindow['Skip'].update(disabled=True)
                replacerWindow['Replace'].update(disabled=True)
                replacerWindow['Next'].update(disabled=True)
                
                psg.popup_ok('Reached end of file.')
        
        # Replaces the current testsuite search with the testsuite match in the favaEngineConfig.
        if event == 'Replace':
            # Replace function
            favaEngineConfigJSON = getNewFavaConfigTestsuiteNames(favaEngineConfigJSON, testsuiteNames[currTestsuite], found[testsuiteNames[currTestsuite]])
            try:
                # Go next
                currTestsuite += 1
                replacerWindow['_search'].Update(str(testsuiteNames[currTestsuite]))
                replacerWindow['_matches'].Update(str(found[testsuiteNames[currTestsuite]]))
                currIter = iter(found[testsuiteNames[currTestsuite]])
                currMatch = next(currIter)
                replacerWindow['_match'].Update(str(currMatch))
            except (StopIteration, IndexError) as e:
                # Disable the buttons to prevent user error.
                replacerWindow['Skip'].update(disabled=True)
                replacerWindow['Replace'].update(disabled=True)
                replacerWindow['Next'].update(disabled=True)

                psg.popup_ok('Reached end of file.')
                    
        # Outputs the changes made to the favaEngineConfig to the searchWindow output.
        if event == 'Output':
            searchWindow['_output'].Update('')
            searchWindow['_output'].Update(dumps(favaEngineConfigJSON, indent=2, default=lambda obj: list(obj) if isinstance(obj, set) else exec('raise TypeError')))
    
    # First in last out garbage collection.
    window.close()
    replacerWindow = None
    searchWindow = None


# Only runs the program if the .py file is ran as main.
# Prevents running the program in the case that this module is imported into another.
if __name__ == '__main__':
    _run()
