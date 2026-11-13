package com.example.example_mod.neoforge;

import com.example.example_mod.ClientMain;
import com.example.example_mod.config.gui.GeneralOptionsScreen;

import net.neoforged.fml.ModContainer;
import net.neoforged.fml.ModList;
import net.neoforged.neoforge.client.gui.IConfigScreenFactory;

final class ClientMainNeoForge {

    private ClientMainNeoForge() {
    }

    static void init(ModContainer container) {
        ClientMain.init();

        if (ModList.get().isLoaded("cloth_config")) {
            container.registerExtensionPoint(IConfigScreenFactory.class,
                    (minecraft, parent) -> GeneralOptionsScreen.create(parent));
        }
    }

}
