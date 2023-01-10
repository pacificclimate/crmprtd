from crmprtd.ec_swob.download import main as swob_main


def main(*args, **kwargs):
    swob_main("dfo-ccg-lighthouse", *args, **kwargs)


if __name__ == "__main__":
    main()
