package com.example.example_mod.fabric.config.gui;

import com.example.example_mod.config.gui.GeneralOptionsScreen;

import com.terraformersmc.modmenu.api.ConfigScreenFactory;
import com.terraformersmc.modmenu.api.ModMenuApi;

import net.fabricmc.loader.api.FabricLoader;

public final class ModMenuIntegration implements ModMenuApi {

    @Override
    public ConfigScreenFactory<?> getModConfigScreenFactory() {
        FabricLoader loader = FabricLoader.getInstance();
        if (!loader.isModLoaded("cloth-config") && !loader.isModLoaded("cloth-config2")) {
            return parent -> null;
        }
        return GeneralOptionsScreen::create;
    }

}
