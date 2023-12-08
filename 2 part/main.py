import concurrent.futures
import logging
from time import time
from multiprocessing import cpu_count


logger = logging.getLogger("time_log")
logger.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG, format='Done in %(message)s sec')


def factorize(*number):
      
    return '\n'.join(f"number {num} dividers: {', '.join(str(i) for i in range(1, num + 1) if num % i == 0)}" for num in number)
    
    
if __name__ == '__main__':
    numbers = 128, 255, 99999, 10651060, 3454, 333, 6764754, 4521321, 67678, 78978, 45, 78889, 6776

    print("\nSyncronic code \n")
    timer = time()
    print(factorize(*numbers))
    logger.debug(f"{time() - timer}")


    print("\nParallel code \n")
    timer2 = time()

    with concurrent.futures.ProcessPoolExecutor(cpu_count()) as executor:
        for number, func in zip(numbers, executor.map(factorize, numbers)):            
            print('%s' % (func))


    logger.debug(f"{time() - timer2}")