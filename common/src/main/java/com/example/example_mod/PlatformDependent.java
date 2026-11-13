package com.example.example_mod;

import dev.architectury.injectables.annotations.ExpectPlatform;

import java.nio.file.Path;

public final class PlatformDependent {

    private PlatformDependent() {
    }

    @ExpectPlatform
    public static Path getConfigDirectory() {
        throw new AssertionError();
    }

}
