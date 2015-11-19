#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define PAGE_SIZE 256
#define PAGE_COUNT 256
#define FRAME_COUNT 256
#define TLB_COUNT 16

int pageNum[PAGE_COUNT];
char pages[PAGE_COUNT][PAGE_SIZE];
char tlbFrames[TLB_COUNT][PAGE_SIZE];
int tlbPages[TLB_COUNT];
int tlbCounter = 0;


int getPage(int arg)
{
	return (arg >> 8) % (1 << 8);
}

int getOffset(int arg)
{
	return arg % (1 << 8);
}

void addToTLB(int index, char *page)
{
	tlbPages[tlbCounter] = index;
	strcpy(tlbFrames[tlbCounter], page);

	++tlbCounter;
	tlbCounter %= TLB_COUNT;
}


//FIFO:	TRUE
//LRU: FALSE
int pageFault(int page)
{
	FILE *bin = fopen("BACKING_STORE.bin", "rb");
	fseek(bin, PAGE_SIZE * page, SEEK_SET);
	fread(pages[page], PAGE_SIZE, 1, bin);
	addToTLB(page, pages[page]);
	pageNum[page] = page;
	fclose(bin);

	return page;
}

int main(int argc, char const *argv[])
{
	for (int i = 0; i < TLB_COUNT; ++i)
	{
		tlbPages[i] = -1;
	}
	for (int i = 0; i < PAGE_COUNT; ++i)
	{
		pageNum[i] = -1;
	}

	FILE *input = fopen(argv[1], "r");
	char str[7];

	int counter = 0;
	double hit = 0;
	double fault = 0;

	while (fgets(str, 7, input) != NULL)
	{
		int arg = atoi(str);
		int page = getPage(arg);
		int offset = getOffset(arg);
		int address = (page << 8) + offset;

		int isHit = 0;

		for (int i = 0; i < TLB_COUNT; ++i)
		{
			if (tlbPages[i] == page)
			{
				printf("TLB Hit!\n");
				printf("Address: %d, Page: %d, Offset: %d, Value: %d\n", address, getPage(arg), getOffset(arg), tlbFrames[i][offset]);
				isHit = 1;
				hit++;
				break;
			}
		}
		if (isHit == 0 && pageNum[page] != -1)
		{
			addToTLB(pageNum[page], pages[page]);
			printf("TLB Miss: Found in memory\n");
			printf("Address: %d, Page: %d, Offset: %d, Value: %d\n", address, getPage(arg), getOffset(arg), pages[page][offset]);
		}
		else if (isHit == 0)
		{
			page = pageFault(page);
			printf("TLB Miss: Fault to %d\n", page);
			printf("Address: %d, Page: %d, Offset: %d, Value: %d\n", address, getPage(arg), getOffset(arg), pages[page][offset]);
			fault++;
		}

		
		isHit = 0;
		counter++;
	}
	printf("Hit Rate: %3f, Fault Rate: %3f\n", hit/counter, fault/counter);

	fclose(input);
	return 0;
}