import queryProcessor
import time

def main():
    qp = queryProcessor.QueryMachine()
    while(True):
        user_q = input("ASK PETE: ")

        start_time = time.time()
        # Retrieving valid urls
        urls = qp.retrieveURLS(user_q)
        pretty_print(urls)

        elapsed = (time.time() - start_time) * 1000
        print(f"Query processing took {elapsed:.2f}ms")
        run_flag = input("\nSearch Again (Y/N)?: ")
        if run_flag[0].lower() == 'n':
            break
        else:
            # clearing their local memory of the inverted index
            qp.inverted_indexes.clear()
    print("Goodbye!")

def pretty_print(urls):
    if len(urls) == 0:
        print("No URLs found")
    else:
        for i in range(min(len(urls), 5)):
            print(f"{i+1}: {urls[i]}")


if __name__ == "__main__":
    main()