package com.example.example_mod.neoforge;

import net.neoforged.fml.loading.FMLPaths;

import java.nio.file.Path;

public final class PlatformDependentImpl {

    private PlatformDependentImpl() {
    }

    public static Path getConfigDirectory() {
        return FMLPaths.CONFIGDIR.get();
    }

}
