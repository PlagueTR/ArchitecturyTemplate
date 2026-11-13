package com.example.example_mod;

import com.example.example_mod.config.ModConfig;
import com.example.example_mod.config.ModConfigManager;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

public final class Main {

    public static final String MOD_ID = "example_mod";
    public static final String MOD_NAME = "Example Mod";
    public static final Logger LOGGER = LogManager.getLogger(MOD_NAME);

    private Main() {
    }

    public static void init() {
        LOGGER.info("Loading...");

        ModConfigManager.load();

        LOGGER.info("All done!");
    }

    public static ModConfig getConfig() {
        return ModConfigManager.getConfig();
    }

    public static void saveConfig() {
        ModConfigManager.save();
    }

}
