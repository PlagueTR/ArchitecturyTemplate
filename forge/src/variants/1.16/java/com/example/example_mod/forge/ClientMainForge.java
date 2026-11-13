package com.example.example_mod.forge;

import com.example.example_mod.ClientMain;
import com.example.example_mod.config.gui.GeneralOptionsScreen;

import net.minecraftforge.fml.ExtensionPoint;
import net.minecraftforge.fml.ModList;
import net.minecraftforge.fml.ModLoadingContext;

final class ClientMainForge {

    private ClientMainForge() {
    }

    static void init() {
        ClientMain.init();

        if (ModList.get().isLoaded("cloth-config")) {
            ModLoadingContext.get().registerExtensionPoint(ExtensionPoint.CONFIGGUIFACTORY,
                    () -> (minecraft, parent) -> GeneralOptionsScreen.create(parent));
        }
    }

}
