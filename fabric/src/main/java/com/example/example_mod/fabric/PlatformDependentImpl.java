package com.example.example_mod.fabric;

import net.fabricmc.loader.api.FabricLoader;

import java.nio.file.Path;

public final class PlatformDependentImpl {

    private PlatformDependentImpl() {
    }

    public static Path getConfigDirectory() {
        return FabricLoader.getInstance().getConfigDir();
    }

}
