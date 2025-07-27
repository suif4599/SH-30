from interface import Case

if __name__ == "__main__":

# Place the official cavity case in the `${FOAM_RUN}/cavity` directory.
# It is assumed that this directory and the related files already exist.

    print("\n" f"{'CreateCase':=^50}" "\n")
    case = Case("${FOAM_RUN}/cavity")
    print(case)

    print("\n" f"{'GetFile':=^50}" "\n")
    blockMeshDict = case["blockMeshDict"]
    print(blockMeshDict)
    print("\nContent:\n")
    print(blockMeshDict.content)
    print("\nParsed Dictionary:\n")
    print(blockMeshDict.dict)

    print("\n" f"{'RunCase':=^50}" "\n")
    case.run()
    print("\nCase Output:\n")
    for info in case.run_info:
        print(info)

    print("\n" f"{'ModifyFile':=^50}" "\n")
    # rename "tp" to "top"
    blockMeshDict.dict["boundary"]["tp"] = blockMeshDict.dict["boundary"]["top"]
    del blockMeshDict.dict["boundary"]["top"]
    blockMeshDict.save()
    print("\nModified Content:\n")
    print(blockMeshDict.content)

    print("\n" f"{'ErrorHandling':=^50}" "\n")
    # Only Test UNMATCHED_FIELD
    print("The case file has been modified above, so there's an unmatched field now.")
    case.run()
    print("\nCase Error:\n")
    print(case.error)


    print("\n" f"{'Rollback':=^50}" "\n")
    print("Snapshots:")
    print(blockMeshDict.snapshots)
    blockMeshDict.rollback(blockMeshDict.snapshots[0]) # earliest snapshot
    print("\nRolled Back Content:\n")
    blockMeshDict.delete_snapshots()  # Clean up snapshots after rollback
    print(blockMeshDict.content)


