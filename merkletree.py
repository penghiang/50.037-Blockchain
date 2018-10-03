import hashlib
from typing import List
# Question 5
# Merkle tree

class MerkleTree():

    class Node():
        # Each node has a parent, a left and a right child.
        # Some nodes (firsthash) only have one child (data)
        def __init__(self, hashvalue: bytes):
            self.data = hashvalue
            self.parent, self.left, self.right = None, None, None
            
        def addparent(self, parent: 'Node'):
            self.parent = parent
        
        def addchildren(self, left: 'Node' = None, right: 'Node' = None):
            self.left = left
            self.right = right


    def add(self, entryData: bytes):
        # Add entries to tree
        self.dataentries.append(entryData)

    def build(self):
        # Build tree computing new root
        self.allnodes = []
        currlevel = []
        temp = None
        for i in self.dataentries:
            hashed = hashlib.sha256(b'0' + i).digest()
            # print(hashed.hex())
            currlevel.append(self.Node(hashed))
        # currlevel first contains all the new nodes
        if(len(currlevel)%2 == 1):
            # We only feed in an even number of currlevels into _build_next_level(),
            # We include the odd one out after building the next level.
            temp = currlevel[-1]
            currlevel = currlevel[:-1]
        # print(str(len(currlevel)) + 'asd')
        self.allnodes += (currlevel)
        nextlevel = self._build_next_level(currlevel)
        # We build the next level and add the current level into allnodes
        if(temp != None):
            # We might append the odd node at the start so it'll be used in the next build.
            # Might give more efficient trees?
            nextlevel.append(temp)
            temp = None

        while(len(nextlevel) > 1):
            # We continuously run _build_next_level() on each level, taking care to only use it on even-numbered lists
            # We omit the odd-numbered node until it has found a pair.
            # i.e. only nodes that are put into _build_next_level() are added to self.allnodes
            currlevel = nextlevel
            nextlevel = []
            if(len(currlevel)%2 == 1):
                # We only feed in an even number of currlevels into _build_next_level(),
                # We include the odd one out after building the next level.
                temp = currlevel[-1]
                currlevel = currlevel[:-1]
            self.allnodes += (currlevel)
            nextlevel = self._build_next_level(currlevel)
            if(temp != None):
                nextlevel.append(temp)
                temp = None
        self.allnodes += nextlevel # This is the last/root node
        # print(len(self.allnodes))
        # allnodes.append(currlevel)
    
    def _build_next_level(self, hashlist: List['Node']) -> List['Node']:
        # This method builds a single level upwards.
        # Since the list passed in has mutable objects, 
        # when we edit hashlist we edit the list outside too.
        # All hashes should be in bytes
        nextlevel = []
        for i in range(len(hashlist)//2):
            i = i*2
            totalhash = b'1' + hashlist[i].data + b'1' + hashlist[i+1].data
            newnode = self.Node(hashlib.sha256(totalhash).digest())
            newnode.addchildren(left=hashlist[i], right=hashlist[i+1])
            hashlist[i].addparent(newnode)
            hashlist[i+1].addparent(newnode)
            nextlevel.append(newnode)
        return nextlevel

    def get_proof(self, entry):
        # Get membership proof for entry
        # Returns a list of a list, innerlist[0] = hash, 
        # innerlist[1] = "r" or "l", indicating the direction it is to be appended to 
        hashlist = []
        if (entry not in self.dataentries):
            return 
        # We look for the entry and its node in self.allnodes
        entryhash = hashlib.sha256(b'0' + entry).digest()
        for i,j in enumerate(self.allnodes):
            if(j.data == entryhash):
                itemindex = i
        currnode = self.allnodes[itemindex]

        # When we find the entry, we can get hashes required for proof
        while(currnode.parent != None):
            prevnode = currnode
            currnode = currnode.parent
            if(currnode.left == prevnode):
                hashlist.append([currnode.right.data, "r"])
            else:
                hashlist.append([currnode.left.data, "l"])
        return hashlist


    def _get_root(self) -> 'Node':
        # Returns the root
        # The root should be the last thing to be added to build()
        self.build()
        return self.allnodes[-1]

    def get_root(self) -> bytes:
        # Returns the root
        # The root should be the last thing to be added to build()
        self.build()
        if(len(self.allnodes) == 0):
            return hashlib.sha256(b'').digest()
        return self.allnodes[-1].data

    def _get_root_2(self) -> 'Node':
        # This method traverses the tree
        # Just an extra get_root method that should be more accurate.
        currnode = self.allnodes[0]
        while(currnode.parent != None):
            currnode = currnode.parent
        return currnode

    def get_entries(self):
        return self.dataentries

    def __init__(self, trnscs: List[bytes] = None):
        self.allnodes = []
        self.dataentries = []
        if(trnscs != None):
            for i in trnscs:
                self.add(i)

def verify_proof(entry, proof, root: bytes):
    # Verifies proof for entry and given root. Returns boolean.
    currhash = hashlib.sha256(b'0' + entry).digest()
    for i in proof:
        if(i[1] == "r"):
            currhash = hashlib.sha256(b'1' + currhash + b'1' + i[0]).digest()
        else:
            currhash = hashlib.sha256(b'1' + i[0] + b'1' + currhash).digest()
    return root == currhash



if __name__ == "__main__":

    x = MerkleTree()
    x.add(b'1')
    x.add(b'second')
    x.add(b'tres')
    x.build()
    assert(len(x.dataentries) == 3)
    assert(len(x.allnodes) == 5)
    # for i in x.allnodes:
        # print(i.data.hex())

    firsthash = hashlib.sha256(b'1' + hashlib.sha256(b'01').digest() + b'1' + hashlib.sha256(b'0second').digest()).digest() 
    assert(firsthash.hex())
    # This hash should be equals to the first hash we get with our formula

    secondhash = hashlib.sha256(b'1' + firsthash + b'1' + hashlib.sha256(b'0tres').digest()).digest()
    assert(secondhash.hex())
    # This hash should be equals the second hash

    x.add(b'umpat')
    x.add(b'quin')
    x.build()
    assert(len(x.dataentries) == 5)
    assert(len(x.allnodes) == 9)
    # print(len(x.allnodes))
    for _ in x.allnodes:
        print(_.data.hex())
    # print(x.get_proof(b'umpat'))
    # If we change get_proof to use .hex() while storing data, we are able to debug this.
    # We can see that b"umpat" uses the 3rd, 5th, and 8th nodes (on L, L and R respectively), 
    # which is consistent if we were to draw this out.

    # Some tests for verify_proof
    assert(verify_proof(b'tres', x.get_proof(b'tres'), x.get_root()))
    assert(verify_proof(b'quin', x.get_proof(b'quin'), x.get_root()))
    assert not (verify_proof(b'second', x.get_proof(b'1'), x.get_root()))
