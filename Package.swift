// swift-tools-version: 5.9

import PackageDescription

let package = Package(
    name: "DockPet",
    platforms: [
        .macOS(.v14)
    ],
    targets: [
        .executableTarget(
            name: "DockPet",
            path: "DockPet",
            exclude: ["Resources"]
        ),
        .testTarget(
            name: "DockPetTests",
            dependencies: ["DockPet"],
            path: "Tests/DockPetTests"
        )
    ]
)
