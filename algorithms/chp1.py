def hasUniqChars(text):
    lets=set()
    for t in text:
        if t in lets:
            return False
        lets.add(t)
    return True

def isPermut(a,b):
    sa= set(a)
    sb= set(b)
    return ((len(sa.difference(sb)) == 0) & 
            (len(sb.difference(sa)) == 0) &
            (len(a) == len(b)))

def compress(text):
    newText= []
    i=0
    while i < len(text):
        cnt=1
        for j in range(i+1,len(text)):
            if text[j]== text[i]:
                cnt+=1
            else:
                break
        newText.append('%s%d' % (text[i],cnt))
        i+= cnt
    newText= "".join(newText)
    print(text,newText)
    if len(newText) < len(text):
        return newText
    else:
        return text


if __name__ == "__main__":
    assert(not hasUniqChars('hello'))
    assert(hasUniqChars('helo'))

    assert(isPermut('hello','elloh'))
    assert(not isPermut('helo','helloh'))

    assert(compress('aabcccccaaa') == 'a2b1c5a3')
    assert(compress('abca') == 'abca')



