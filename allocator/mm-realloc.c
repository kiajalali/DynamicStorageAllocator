/**
 * CMPT 295 Assignment Malloc
 *
 * Extra credit: implementing mm_realloc
 *
 * This requires mm_malloc and mm_free to be working correctly, so
 * don't start on this until you finish mm.c.
 */
#include "mm.c"

// Extra credit.
void *mm_realloc(void *ptr, size_t size)
{
    // Write your code here ...
    BlockInfo *blockInfo = (BlockInfo*) UNSCALED_POINTER_SUB(ptr, WORD_SIZE);
    size_t sz = SIZE(blockInfo->sizeAndTags) - WORD_SIZE;

    // cover edges
    if (ptr == NULL) return mm_malloc(size);
    
    if (size == 0) {
        mm_free(ptr);
        return NULL;
    }

    // we need a place to store the data after resizing
    ptr = mm_malloc(size);

    // checking the size
    size_t currSize;
    if (size <= sz) currSize = size;
    else currSize = sz;

    // we need this for out copy since we cant use stdlib functions 
    void *pointToData = UNSCALED_POINTER_ADD(blockInfo, WORD_SIZE);
    
    char *copyTo = (char*) ptr, *copyFrom = (char*) pointToData;
    // copy the data to the new list
    for (int i = 0; i < size; i++) copyTo[i] = copyFrom[i];
    
    // free the old list
    mm_free(UNSCALED_POINTER_ADD(blockInfo, WORD_SIZE));
    return ptr;
}
