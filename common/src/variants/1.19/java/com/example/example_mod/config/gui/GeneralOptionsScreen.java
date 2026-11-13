package com.example.example_mod.config.gui;

import com.example.example_mod.Main;
import com.example.example_mod.config.ModConfig;

import me.shedaniel.clothconfig2.api.ConfigBuilder;
import me.shedaniel.clothconfig2.api.ConfigCategory;
import me.shedaniel.clothconfig2.api.ConfigEntryBuilder;

import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;

public final class GeneralOptionsScreen {

    private GeneralOptionsScreen() {
    }

    public static Screen create(Screen parent) {
        ModConfig defaults = new ModConfig();

        ConfigBuilder builder = ConfigBuilder.create()
                .setParentScreen(parent)
                .setTitle(Component.literal(Main.MOD_NAME))
                .setSavingRunnable(Main::saveConfig);
        builder.transparentBackground();

        ConfigEntryBuilder entryBuilder = builder.entryBuilder();
        ConfigCategory general = builder.getOrCreateCategory(Component.literal("General"));

        general.addEntry(entryBuilder.startBooleanToggle(Component.literal("Enable Mod"), Main.getConfig().isEnableMod())
                .setDefaultValue(defaults.isEnableMod())
                .setTooltip(Component.literal("Master switch to turn all mod features on or off."))
                .setSaveConsumer(Main.getConfig()::setEnableMod)
                .build());

        return builder.build();
    }

}
