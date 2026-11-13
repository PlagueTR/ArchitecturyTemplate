package com.example.example_mod.forge;

import com.example.example_mod.ClientMain;
import com.example.example_mod.config.gui.GeneralOptionsScreen;

import net.minecraftforge.client.ConfigScreenHandler;
import net.minecraftforge.fml.ModList;
import net.minecraftforge.fml.ModLoadingContext;

final class ClientMainForge {

    private ClientMainForge() {
    }

    static void init() {
        ClientMain.init();

        if (ModList.get().isLoaded("cloth_config")) {
            ModLoadingContext.get().registerExtensionPoint(ConfigScreenHandler.ConfigScreenFactory.class,
                    () -> new ConfigScreenHandler.ConfigScreenFactory((minecraft, parent) -> GeneralOptionsScreen.create(parent)));
        }
    }

}
