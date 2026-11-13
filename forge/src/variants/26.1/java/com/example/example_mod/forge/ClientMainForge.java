package com.example.example_mod.forge;

import com.example.example_mod.ClientMain;
import com.example.example_mod.config.gui.GeneralOptionsScreen;

import net.minecraftforge.client.ConfigScreenHandler;
import net.minecraftforge.fml.ModList;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;

final class ClientMainForge {

    private ClientMainForge() {
    }

    static void init(FMLJavaModLoadingContext context) {
        ClientMain.init();

        if (ModList.isLoaded("cloth_config")) {
            context.registerExtensionPoint(ConfigScreenHandler.ConfigScreenFactory.class,
                    () -> new ConfigScreenHandler.ConfigScreenFactory((minecraft, parent) -> GeneralOptionsScreen.create(parent)));
        }
    }

}
