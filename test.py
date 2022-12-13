if __name__ == "__main__":
    robolisto = []
    for num in range(5):
        robolisto.append(num)

    [robolisto.append(r) for r in range(5)]
    print(robolisto)