This is part two of the smart contract parsing script in Python. The script continues the analysis of a given smart contract and extracts crucial information. The document structure is updated with new keys for storing different types of data. 

The script defines several functions that analyze and extract the following information:
* Function-related data: visibility, modifiers, and names.
* Libraries used by the contract and their relevant attributes.
* Details of contracts, abstract contracts, and interfaces, including their attributes, addresses, names, and whether they are declared or not.
* Information related to the contract constructor, defining how the contract is initialized and what attributes it requires.
* The initial variables of the contract, identifying if they are of types like address, uint, string, bool, and extracting their details.
* The attributes of a contract and where they are leveraged.
* The lines in the contract where particular keywords are found.

The data is continuously updated to a file `LineTrack.json` which keeps track of the lines of code and the data found on each line. This part of the script is vital for understanding the dependencies, structure, and functionality of the smart contract.

