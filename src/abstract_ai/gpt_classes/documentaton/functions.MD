This script chunk, which is the fifth of nine, contains additional utility functions for processing a smart contract. These functions include reading files, splitting data, determining section of the script, checking if an item is in a list, creating and reading JSON files, handling data types, and more functions for querying and manipulating specific aspects of smart contracts.

The `get_syntax_info()` function returns a dictionary with the required syntax information for smart contracts. The keys include 'names', 'Modifiers', 'precedence', 'visibility', 'globalVariables', and others, with their corresponding values.

There are also declarations of functions for specialized operations, like checking if two values are above zero (`ifBothOverZero()`), getting just higher value (`getJustHigher()`), converting a list to a string (`linesToString()`), and making sure a script stops when closed (`stopWhenClosed()`).

Towards the end of the script chunk, a class `contractVariablesManager` is declared. This class is initialized with the current file path (currFilePath), a lineTrack dictionary, and lines of code. It contains a variety of methods for manipulating and accessing individual aspects of a smart contract, such as a method that returns all lines (`allLinesParse()`), or a method that processes the attribute value (`checkAttributeValue()`), and more.

Overall, this script is essential for the main utility of parsing and launching smart contracts smoothly and accurately.
