from crmprtd.networks.ec_swob.download import main as swob_main


def main(*args, **kwargs):
    swob_main("bc-tran", *args, **kwargs)


if __name__ == "__main__":
    main()
